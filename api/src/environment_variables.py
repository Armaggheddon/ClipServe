import os
from enum import Enum

class EnvironmentKeys(Enum):
    SHOW_API_DOCS = "SHOW_API_DOCS"


def should_show_api_docs():
    show_docs = os.environ.get(EnvironmentKeys.SHOW_API_DOCS.value, "True")
    bool_show_docs = True if show_docs in ["True", "true", "1"] else False
    return bool_show_docs