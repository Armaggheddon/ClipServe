from typing import List, Union, Optional
import redis.asyncio as redis
import redis_models

class RedisManager():
    """
    Manager class for interacting with Redis
    using the aioredis library for async operations
    """
    def __init__(self, host: str, port:str, decode_responses: bool=False):
        """
        Constructor for the RedisManager class
        
        Args:
        - host (str): The host of the Redis server
        - port (str): The port of the Redis server
        - decode_responses (bool): Whether to decode responses or not
        """
        self.host = host
        self.port = port
        self.decode_responses = decode_responses

        redis_url = f"redis://{host}:{port}"
        self.pool = redis.ConnectionPool.from_url(url=redis_url, decode_responses=decode_responses)
        self.redis_client = redis.Redis.from_pool(self.pool)

    async def ping(self) -> bool:
        """
        Ping the Redis server to check if it is up
        
        Returns:
        - bool: True if the server is up, False otherwise
        """
        return await self.redis_client.ping()

    async def close(self):
        """
        Close the connection to the Redis server
        """
        await self.redis_client.aclose()

    async def enqueue_job(
            self, 
            job_id: str, 
            texts: Optional[Union[str, List[str]]] = None, 
            images: Optional[Union[str, List[str]]] = None):
        """
        Enqueue a job to the Redis server using the 
        `requests` queue.

        Args:
        - job_id (str): The ID of the job
        - texts (Union[str, List[str]]): The text to be enqueued
        - images (Union[str, List[str]]): The images to be enqueued
        """

        if texts is None: texts = []
        if images is None: images = []

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

        # Push the data to the requests queue head
        await self.redis_client.lpush(f"requests", redis_data.to_json())

    async def get_result(self, job_id: str) -> str:
        """
        Get the result of a job from the Redis server,
        awaits the queue named `{job_id}-response` for the result
        
        Args:
        - job_id (str): The ID of the job
        
        Returns:
        - str: The Redis response item as a JSON string
        """
        while True:
            # When calling brprop, the result is a tuple of 2 elements
            # The first element is the key of the list, 
            # the second element is the value of the list   
            result = await self.redis_client.brpop(f"{job_id}-response", timeout=1)
            if result is not None:
                return result[1]
            else:
                continue