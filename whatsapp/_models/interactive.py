from enum import Enum
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field, constr, root_validator
from .media import Media


class InteractiveTypes(str, Enum):
    LIST = "list"
    BUTTON = "button"
    PRODUCT = "product"
    PRODUCT_LIST = "product_list"


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
    description: Optional[constr(max_length=72)]


class ButtonRow(Row):
    title: constr(max_length=20)


class SectionRow(Row):
    title: constr(max_length=23)


class Button(BaseModel):
    type: str = "reply"
    reply: ButtonRow


class Section(BaseModel):
    title: str
    rows: List[SectionRow]


class Action(BaseModel):
    button: Optional[Button]
    buttons: Optional[List[Button]]
    sections: Optional[List[Section]]


class ListAction(Action):
    button: str
    sections: List[Section]


class ButtonsAction(Action):
    buttons: List[Button]


class Interactive(BaseModel):
    type: InteractiveTypes
    body: Text
    footer: Optional[Text]
    header: Optional[Header]
    action: Union[ListAction, ButtonsAction]

    class Config:
        use_enum_values = True


class InteractiveList(Interactive):
    type: InteractiveTypes = InteractiveTypes.LIST
    action: ListAction


class InteractiveButtons(Interactive):
    type: InteractiveTypes = InteractiveTypes.BUTTON
    action: ButtonsAction
