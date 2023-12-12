from enum import Enum
from typing import Optional

from pydantic import BaseModel, constr


class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    INTERACTIVE = "interactive"
    TEMPLATE = "template"
    CONTACTS = "contacts"
    REACTION = "reaction"


class TextFont(str, Enum):
    SANS_SERIF = "SANS_SERIF"
    SERIF = "SERIF"
    NORICAN_REGULAR = "NORICAN_REGULAR"
    BRYNDAN_WRITE = "BRYNDAN_WRITE"
    BEBASNEUE_REGULAR = "BEBASNEUE_REGULAR"
    OSWALD_HEAVY = "OSWALD_HEAVY"


class Text(BaseModel):
    body: constr(min_length=1)
    font: Optional[TextFont] = None
    background_color: Optional[str] = None
    text_color: Optional[str] = None

    class Config:
        use_enum_values = True
