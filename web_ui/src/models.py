from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional


class ZeroShotClassificationRequest(BaseModel):
    """
    ZeroShotClassificationRequest model, used to send
    labels and images to the API and get the classification
    results.
    Example:
    ```json
    {
        "labels": ["dog", "cat"],
        "images_b64": ["base64 encoded image"]
    }
    ```
    """
    labels: List[str] = Field(default_factory=list)
    images_b64: List[str] = Field(default_factory=list)

    def to_json(self):
        return self.model_dump_json()


class ImageEmbedding(BaseModel):
    """
    ImageEmbedding model, used to store the image embeddings
    """
    image_id: str
    embedding: List[float]

class TextEmbedding(BaseModel):
    """
    TextEmbedding model, used to store the text embeddings
    """
    text: str
    embedding: List[float]

class SoftmaxOutput(BaseModel):
    """
    SoftmaxOutput model, used to store the softmax scores for
    a classification task
    """
    image_id: str
    softmax_scores: List[float]

class ClassificationResult(BaseModel):
    """
    ClassificationResult model, used to store the classification
    results
    """
    labels: List[str] = Field(default_factory=list)
    softmax_outputs: List[SoftmaxOutput] = Field(default_factory=list)
    

class RedisResponseItem(BaseModel):
    """
    RedisResponseItem model, used to store the response data
    for every job in the Redis server
    
    Example:
    ```json
    {
        "status": "success",
        "text_embeddings": [
            {
            "text": "a photo of a cat",
            "embedding": [0.12, 0.21, 0.38, ..., 0.512]
            }
        ],
        "image_embeddings": [
            {
            "image_id": "36d2e446-e5ad-423e-a847-b7da1a2b4d70",
            "embedding": [0.44, 0.55, 0.61, ..., 0.512]
            },
            {
            "image_id": "f1b87bfe-9b1c-4f93-b87d-1a51fb9e5795",
            "embedding": [0.34, 0.52, 0.68, ..., 0.512]
            }
        ],
        "classification_results": {
            "labels": ["cat", "dog", "bird"],
            "softmax_outputs": [
            {
                "image_id": "36d2e446-e5ad-423e-a847-b7da1a2b4d70",
                "softmax_scores": [0.7, 0.2, 0.1]
            },
            {
                "image_id": "f1b87bfe-9b1c-4f93-b87d-1a51fb9e5795",
                "softmax_scores": [0.1, 0.3, 0.6]
            }
            ]
        }
    }
    ```
    """
    model_config  = ConfigDict(protected_namespaces=())
    model_name: str
    text_embeddings: Optional[List[TextEmbedding]] = None
    image_embeddings: Optional[List[ImageEmbedding]] = None
    classification_result: Optional[ClassificationResult] = None

    def to_json(self):
        return self.model_dump_json(exclude_unset=True)
    
    @staticmethod
    def from_json(json_data):
        return RedisResponseItem.model_validate_json(json_data)