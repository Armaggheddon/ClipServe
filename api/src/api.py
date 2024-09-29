import uuid
import json
import base64
from typing import List, Union, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI

import models
from redis_manager import RedisManager
from environment_variables import should_show_api_docs


async def write_images(images_path: Optional[List[str]] = None, images_b64: Optional[List[str]] = None):
    """
    Write images to disk from base64 encoded strings
    
    Args:
    - images_path (List[str]): List of paths to write the images
    - images_b64 (List[str]): List of base64 encoded images
    """

    if images_path is None or images_b64 is None:
        return
    
    for img_path, img_data in zip(images_path, images_b64):
        with open(img_path, "wb") as f:
            f.write(base64.b64decode(img_data))


redis_helper: Union[RedisManager, None] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_helper
    redis_helper = RedisManager("redis", 6379)
    await redis_helper.ping()

    yield

    await redis_helper.close()

description = """
API for serving CLIP embeddings. Includes 3 endpoints:
- **embed-text:** Embeds one or more text
- **embed-images:** Embeds one or more images
- **zero-shot-classification:** Classifies images based on provided text labels
"""

app = FastAPI(
    lifespan=lifespan,
    title="ClipServe API",
    description=description,
    version="1.0.0",
    contact={
        "name": "ClipServe",
        "url": "https://github.com/Armaggheddon/ClipServe",
    },
    docs_url="/docs" if should_show_api_docs() else None,
    redoc_url=None,
)



@app.post("/embed-text", response_model=models.TextEmbeddingResponse)
async def embed_text(request: models.TextRequest):
    """
    Embed text using the CLIP model
    """
    text = request.text

    job_id = str(uuid.uuid4())

    # enqueue the text to be embedded
    await redis_helper.enqueue_job(job_id, texts=text)

    # when the result comes back, return the response
    result = await redis_helper.get_result(job_id)
    return json.loads(result)

@app.post("/embed-images", response_model=models.ImageEmbeddingResponse)
async def embed_image(request: models.ImageRequest):
    """
    Embed images using the CLIP model
    """
    img_base64 = request.image_b64

    job_id = str(uuid.uuid4())
    # get image format
    # sample header for base64 image data:image/png;base64,...
    if isinstance(img_base64, str):
        img_base64 = [img_base64]
    
    images_format = [
        img.split(",")[0].split("/")[1].split(";")[0] 
        for img in img_base64]
    
    images_data = [img.split(",")[1] for img in img_base64]
    
    images_path = [
        f"/img_store/{job_id}_{_id}.{format}" 
        for _id, format in enumerate(images_format)]

    await write_images(images_path, images_data)

    # enqueue the text to be embedded
    await redis_helper.enqueue_job(job_id, images=images_path)

    # when the result comes back, return the response
    result = await redis_helper.get_result(job_id)
    
    return json.loads(result)

@app.post("/zero-shot-classification", response_model=models.ClassificationResponse)
async def zero_shot_classification(request: models.ZeroShotClassificationRequest):
    """
    Zero-shot classification using the CLIP model
    """
    labels = request.labels
    img_base64 = request.images_b64

    job_id = str(uuid.uuid4())
    # get image format
    # sample header for base64 image data:image/png;base64
    images_format = [
        img.split(",")[0].split("/")[1].split(";")[0] 
        for img in img_base64]

    images_data = [img.split(",")[1] for img in img_base64]

    images_path = [
        f"/img_store/{job_id}_{_id}.{format}" 
        for _id, format in enumerate(images_format)]

    await write_images(images_path, images_data)

    # enqueue the text to be embedded
    await redis_helper.enqueue_job(job_id, texts=labels, images=images_path)

    # when the result comes back, return the response
    result = await redis_helper.get_result(job_id)
    
    return json.loads(result)
