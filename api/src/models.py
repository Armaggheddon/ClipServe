from pydantic import BaseModel, Field
from typing import List, Union


class TextRequest(BaseModel):
    text: Union[str, List[str]] = Field(default_factory=list)

class ImageRequest(BaseModel):
    image_b64: Union[str, List[str]] = Field(default_factory=list)

class ZeroShotClassificationRequest(BaseModel):
    labels: List[str] = Field(default_factory=list)
    images_b64: List[str] = Field(default_factory=list)