import asyncio
import uuid
from fastapi import FastAPI, HTTPException
import redis.asyncio as redis
import json
import base64
from contextlib import asynccontextmanager
from typing import List, Union
import models
from redis_helper import RedisHelper
from redis_models import RedisResponseItem


async def write_images(images_path: List[str], images_b64: List[str]):
    
    for img_path, img_data in zip(images_path, images_b64):
        with open(img_path, "wb") as f:
            f.write(base64.b64decode(img_data))


redis_helper: Union[RedisHelper, None] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_helper
    redis_helper = RedisHelper("redis", 6379)
    await redis_helper.ping()

    yield

    await redis_helper.close()


app = FastAPI(lifespan=lifespan)


@app.post("/embed-text", response_model=RedisResponseItem)
async def embed_text(request: models.TextRequest):
    text = request.text

    job_id = str(uuid.uuid4())

    # enqueue the text to be embedded
    await redis_helper.enqueue_job(job_id, texts=text)

    # when the result comes back, return the response
    result = await redis_helper.get_result(job_id)
    return json.loads(result)

@app.post("/embed-images", response_model=RedisResponseItem)
async def embed_image(request: models.ImageRequest):
    img_base64 = request.image_b64

    job_id = str(uuid.uuid4())
    # get image format
    # sample header for base64 image data:image/png;base64
    images_format = [
        img.split(",")[0].split("/")[1].split(";")[0] for img in img_base64
    ]

    images_data = [
        img.split(",")[1] for img in img_base64
    ]

    images_path = [
        f"/img_store/{job_id}_{_id}.{format}" for _id, format in enumerate(images_format)
    ]

    await write_images(images_path, images_data)

    # enqueue the text to be embedded
    await redis_helper.enqueue_job(job_id, images=images_path)

    # when the result comes back, return the response
    result = await redis_helper.get_result(job_id)
    
    return json.loads(result)

@app.post("/zero-shot-classification", response_model=RedisResponseItem)
async def zero_shot_classification(request: models.ZeroShotClassificationRequest):
    
    labels = request.labels
    img_base64 = request.images_b64

    job_id = str(uuid.uuid4())
    # get image format
    # sample header for base64 image data:image/png;base64
    images_format = [
        img.split(",")[0].split("/")[1].split(";")[0] for img in img_base64
    ]

    images_data = [
        img.split(",")[1] for img in img_base64
    ]

    images_path = [
        f"/img_store/{job_id}_{_id}.{format}" for _id, format in enumerate(images_format)
    ]

    await write_images(images_path, images_data)

    # enqueue the text to be embedded
    await redis_helper.enqueue_job(job_id, texts=labels, images=images_path)

    # when the result comes back, return the response
    result = await redis_helper.get_result(job_id)
    
    return json.loads(result)
