from pydantic import BaseModel, Field
from typing import List, Optional


class ZeroShotClassificationRequest(BaseModel):
    labels: List[str] = Field(default_factory=list)
    images_b64: List[str] = Field(default_factory=list)

    def to_json(self):
        return self.model_dump_json()

class ImageEmbedding(BaseModel):
    image_id: str
    embedding: List[float]

class TextEmbedding(BaseModel):
    text: str
    embedding: List[float]

class SoftmaxOutput(BaseModel):
    image_id: str
    softmax_scores: List[float]

class ClassificationResult(BaseModel):
    labels: List[str] = Field(default_factory=list)
    softmax_outputs: List[SoftmaxOutput] = Field(default_factory=list)
    

class RedisResponseItem(BaseModel):
    text_embeddings: Optional[List[TextEmbedding]] = None
    image_embeddings: Optional[List[ImageEmbedding]] = None
    classification_result: Optional[ClassificationResult] = None

    def to_json(self):
        return self.model_dump_json(exclude_unset=True)
    
    @staticmethod
    def from_json(json_data):
        return RedisResponseItem.model_validate_json(json_data)