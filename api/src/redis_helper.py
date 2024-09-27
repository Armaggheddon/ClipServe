import asyncio
from typing import List, Union
import redis.asyncio as redis
import redis_models

class RedisHelper():
    def __init__(self, host, port, decode_responses=False):
        self.host = host
        self.port = port
        self.decode_responses = decode_responses

        redis_url = f"redis://{host}:{port}"
        self.pool = redis.ConnectionPool.from_url(url=redis_url, decode_responses=decode_responses)
        self.redis_client = redis.Redis.from_pool(self.pool)

    async def ping(self):
        return await self.redis_client.ping()

    async def close(self):
        await self.redis_client.aclose()

    async def enqueue_job(self, job_id: str, texts: Union[str, List[str]] = [], images: Union[str, List[str]] = []):
        _texts = []

        if isinstance(texts, str):
            _texts.append(texts)
        elif isinstance(texts, list):
            _texts.extend(texts)
        else:
            raise ValueError("Invalid type for texts, expected str or list of str")
        
        _images = []

        if isinstance(images, str):
            images.append(images)
        elif isinstance(images, list):
            _images.extend(images)
        else:
            raise ValueError("Invalid type for images, expected str or list of str")

        redis_data = redis_models.RedisRequestItem(
            job_id=job_id,
            texts=[redis_models.RedisTextItem(text=text) for text in _texts],
            images=[redis_models.RedisImageItem(image_path=image) for image in _images]
        )

        await self.redis_client.lpush(f"requests", redis_data.to_json())

    async def get_result(self, job_id) -> redis_models.RedisResponseItem:
        while True:
            # When calling brprop, the result is a tuple of 2 elements
            # The first element is the key of the list, 
            # the second element is the value of the list   
            result = await self.redis_client.brpop(f"{job_id}-response", timeout=1)
            if result is not None:
                return result[1]
            else:
                continue