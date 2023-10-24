from pydantic import BaseModel, Field
from typing import Any, Dict, Literal, Optional, Union, List
from enum import Enum
from .media import Thumbnail


class TemplateLanguage(BaseModel):
    policy: str
    code: str


class TemplateComponentType(Enum):
    header = "header"
    body = "body"
    button = "button"


class Media(BaseModel):
    id: Optional[str]
    link: Optional[str]
    caption: Optional[str]
    filename: Optional[str]
    thumbnail: Optional[Thumbnail]


class Currency(BaseModel):
    fallback_value: str = Field(..., description="Default text if localization fails.")
    code: str = Field(..., description="Currency code as defined in ISO 4217.")
    amount_1000: str = Field(..., description="Amount multiplied by 1000.")


class DateTime(BaseModel):
    fallback_value: str = Field(
        ...,
        description="Default text. For Cloud API, we always use the fallback value, and we do not attempt to localize using other optional fields.",
    )


class Action(BaseModel):
    """Action is a special type of parameter that is used to define a button action for flows."""

    flow_token: Optional[str]
    flow_action_data: Optional[Dict[str, Any]]


class TemplateParameter(BaseModel):
    type: Literal[
        "text",
        "currency",
        "date_time",
        "image",
        "document",
        "video",
        "payload",
        "action",
    ]
    text: Optional[str]
    image: Optional[Media]
    document: Optional[Media]
    video: Optional[Media]
    currency: Optional[Currency]
    date_time: Optional[DateTime]
    payload: Optional[str]
    action: Optional[Action]


class TemplateComponent(BaseModel):
    type: TemplateComponentType
    sub_type: Optional[Literal["quick_reply", "url", "flow"]]
    index: Optional[int]
    parameters: Optional[List[TemplateParameter]]


class Template(BaseModel):
    name: str
    namespace: Optional[str]
    language: TemplateLanguage
    components: Optional[List[TemplateComponent]]
