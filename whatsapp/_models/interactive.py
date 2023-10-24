from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
import uuid

from pydantic import BaseModel, Field, constr, root_validator
from .media import Media


class InteractiveTypes(str, Enum):
    LIST = "list"
    BUTTON = "button"
    PRODUCT = "product"
    PRODUCT_LIST = "product_list"
    FLOW = "flow"


class HeaderTypes(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"


class Text(BaseModel):
    text: str


class Header(BaseModel):
    type: HeaderTypes
    text: Optional[Text]
    video: Optional[Media]
    image: Optional[Media]
    document: Optional[Media]


class Row(BaseModel):
    id: str
    title: str


class ButtonRow(Row):
    title: constr(max_length=20)


class SectionRow(Row):
    title: constr(max_length=23)
    description: Optional[constr(max_length=72)]


class Button(BaseModel):
    type: str = "reply"
    reply: ButtonRow


class Section(BaseModel):
    title: str
    rows: List[SectionRow]


class ParametersPayload(BaseModel):
    screen: str
    data: Optional[Dict[str, Any]]


class Parameters(BaseModel):
    mode: Literal["draft", "published"]
    flow_message_version: int = 3
    flow_token: str = Field(
        description="A unique token that identifies the flow message.",
        default_factory=lambda: str(uuid.uuid4()),
    )
    flow_id: str
    flow_cta: str
    flow_action: Literal["navigate", "data_exchange"]
    flow_action_payload: Optional[ParametersPayload]

    @root_validator
    def validate_payload_when_action_is_navigate(cls, values):
        if values.get("flow_action") == "navigate" and not values.get(
            "flow_action_payload"
        ):
            raise ValueError(
                "flow_action_payload is required when flow_action is navigate"
            )

        return values


class Action(BaseModel):
    button: Optional[Button]
    buttons: Optional[List[Button]]
    sections: Optional[List[Section]]
    parameters: Optional[Parameters]


class ListAction(Action):
    button: str
    sections: List[Section]


class ButtonsAction(Action):
    buttons: List[Button]


class FlowAction(Action):
    name: str = "flow"
    parameters: Parameters


class Interactive(BaseModel):
    type: InteractiveTypes
    body: Text
    footer: Optional[Text]
    header: Optional[Header]
    action: Union[ListAction, ButtonsAction, FlowAction]

    class Config:
        use_enum_values = True


class InteractiveList(Interactive):
    type: InteractiveTypes = InteractiveTypes.LIST
    action: ListAction


class InteractiveButtons(Interactive):
    type: InteractiveTypes = InteractiveTypes.BUTTON
    action: ButtonsAction


class InteractiveFlow(Interactive):
    type: InteractiveTypes = InteractiveTypes.FLOW
    action: FlowAction
