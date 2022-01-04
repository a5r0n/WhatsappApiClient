from enum import Enum

from pydantic import BaseModel, constr


class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    INTERACTIVE = "interactive"


class Text(BaseModel):
    body: constr(min_length=1, max_length=1024)
