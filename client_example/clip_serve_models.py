from pydantic import BaseModel, Field, ConfigDict
from typing import List, Union

"""
Request models
"""
class TextRequest(BaseModel):
    """
    TextRequest model, used to send text to the API
    and get the embeddings. 
    Example:
    ```json
    {
        "text": "a photo of a cat"
    }
    ```
    """
    text: Union[str, List[str]] = Field(default_factory=list)

    def to_json(self):
        return self.model_dump_json()


class ImageRequest(BaseModel):
    """
    ImageRequest model, used to send image to the API
    and get the embeddings.
    Example:
    ```json
    {
        "image_b64": "base64 encoded image"
    }
    ```
    """
    image_b64: Union[str, List[str]] = Field(default_factory=list)

    def to_json(self):
        return self.model_dump_json()


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


################################################################################

"""
Response models
"""
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


class TextEmbeddingResponse(BaseModel):
    """
    TextEmbeddingResponse model, response format for text embeddings.
    Example:
    ```json
    {
        "model_name": "clip",
        "text_embeddings": [
            {
                "text": "a photo of a cat",
                "embedding": [0.12, 0.21, 0.38, ..., 0.512]
            },
            ...
        ]
    }
    ```
    """
    model_config  = ConfigDict(protected_namespaces=())
    model_name: str
    text_embeddings: List[TextEmbedding] = Field(default_factory=list)


class ImageEmbeddingResponse(BaseModel):
    """
    ImageEmbeddingResponse model, response format for image embeddings.
    Example:
    ```json
    {
        "model_name": "clip",
        "image_embeddings": [
            {
                "image_id": "36d2e446-e5ad-423e-a847-b7da1a2b4d70",
                "embedding": [0.44, 0.55, 0.61, ..., 0.512]
            },
            ...
        ]
    }
    ```
    """
    model_config  = ConfigDict(protected_namespaces=())
    model_name: str
    image_embeddings: List[ImageEmbedding] = Field(default_factory=list)


class ClassificationResponse(BaseModel):
    """
    ClassificationResponse model, response format for classification results.
    Example:
    ```json
    {
        "model_name": "clip",
        "text_embeddings": [
            {
                "text": "cat",
                "embedding": [0.12, 0.21, 0.38, ..., 0.512]
            },
            ...
        ],
        "image_embeddings": [
            {
                "image_id": "36d2e446-e5ad-423e-a847-b7da1a2b4d70",
                "embedding": [0.44, 0.55, 0.61, ..., 0.512]
            },
            ...
        ],
        "classification_result": {
            "labels": ["cat", "dog", "bird"],
            "softmax_outputs": [
                {
                    "image_id": "36d2e446-e5ad-423e-a847-b7da1a2b4d70",
                    "softmax_scores": [0.7, 0.2, 0.1]
                },
                ...
            ]
        }
    }
    ```
    """
    model_config  = ConfigDict(protected_namespaces=())
    model_name: str
    text_embeddings: List[TextEmbedding] = Field(default_factory=list)
    image_embeddings: List[ImageEmbedding] = Field(default_factory=list)
    classification_result: ClassificationResult = Field(default_factory=list)