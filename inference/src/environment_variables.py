import os
from enum import Enum

class EnvironmentKeys(Enum):
    CLIP_MODEL_NAME = "CLIP_MODEL_NAME"

valid_clip_model_names = [
    "openai/clip-vit-base-patch32",
    "openai/clip-vit-large-patch14",
    "openai/clip-vit-base-patch16",
    "openai/clip-vit-large-patch14-336",
]


def get_clip_model_name():
    """
    Get the CLIP model name from the environment variables
    """
    clip_model_name = os.environ.get(EnvironmentKeys.CLIP_MODEL_NAME.value, valid_clip_model_names[0])
    if clip_model_name not in valid_clip_model_names:
        print(f"Invalid CLIP model name. Valid values are: {valid_clip_model_names}")
        print(f"Using default value: {valid_clip_model_names[0]}")
        clip_model_name = valid_clip_model_names[0]
    
    return clip_model_name