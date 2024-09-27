from pydantic import BaseModel, Field
from typing import List, Optional, Union

class RedisImageItem(BaseModel):
    image_path: str

class RedisTextItem(BaseModel):
    text: str

class RedisRequestItem(BaseModel):
    job_id: str
    texts: Optional[List[RedisTextItem]] = Field(default_factory=list)
    images: Optional[List[RedisImageItem]] = Field(default_factory=list) 

    def to_json(self):
        return self.model_dump_json()
    
    @staticmethod
    def from_json(json_data):
        return RedisRequestItem.model_validate_json(json_data)
    
class RedisResponseItem(BaseModel):
    job_id: str
    text_embeddings: Optional[List[List[float]]] = Field(default_factory=list)
    image_embeddings: Optional[List[List[float]]] = Field(default_factory=list)

    def to_json(self):
        return self.model_dump_json()
    
    @staticmethod
    def from_json(json_data):
        return RedisResponseItem.model_validate_json(json_data)