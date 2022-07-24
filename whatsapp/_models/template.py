from pydantic import BaseModel, Field
from typing import Any, Dict, Literal, Optional, Union, List
from enum import Enum


class TemplateLanguage(BaseModel):
    policy: str
    code: str


class TemplateComponentType(Enum):
    header = "header"
    body = "body"
    button = "button"


class TemplateParameter(BaseModel):
    type: Literal[
        "text", "currency", "date_time", "image", "document", "video", "payload"
    ]
    text: Optional[str]
    payload: Optional[str]


class TemplateComponent(BaseModel):
    type: TemplateComponentType
    sub_type: Optional[Literal["quick_reply", "url"]]
    index: Optional[int]
    parameters: Optional[List[TemplateParameter]]


class Template(BaseModel):
    name: str
    namespace: Optional[str]
    language: TemplateLanguage
    components: Optional[List[TemplateComponent]]
