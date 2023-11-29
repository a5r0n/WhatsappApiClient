from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
import uuid

from pydantic import BaseModel, Field, conlist, constr, root_validator, validator
from .media import Media


class InteractiveTypes(str, Enum):
    LIST = "list"
    BUTTON = "button"
    PRODUCT = "product"
    PRODUCT_LIST = "product_list"
    FLOW = "flow"
    CATALOG_MESSAGE = "catalog_message"


class HeaderTypes(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"


class Text(BaseModel):
    text: str


class Header(BaseModel):
    type: HeaderTypes
    text: Optional[Union[Text, str]]
    video: Optional[Media]
    image: Optional[Media]
    document: Optional[Media]


class TextHeader(Header):
    type: Literal[HeaderTypes.TEXT] = HeaderTypes.TEXT
    text: str


class Row(BaseModel):
    id: str
    title: str


class ButtonRow(Row):
    title: constr(max_length=20)


class SectionRow(Row):
    title: constr(max_length=23)
    description: Optional[constr(max_length=72)]


class ProductItem(BaseModel):
    product_retailer_id: str


class Button(BaseModel):
    type: str = "reply"
    reply: ButtonRow


class Section(BaseModel):
    title: Optional[str]
    rows: Optional[List[SectionRow]]
    product_items: Optional[List[ProductItem]]


class ListSection(Section):
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


class ProductSection(Section):
    product_items: List[ProductItem]


class CatalogMessageActionParameters(BaseModel):
    thumbnail_product_retailer_id: str


class Action(BaseModel):
    name: Optional[str]
    button: Optional[Button]
    buttons: Optional[List[Button]]
    sections: Optional[List[Section]]
    parameters: Optional[Parameters]
    catalog_id: Optional[str]
    product_retailer_id: Optional[str]
    parameters: Optional[CatalogMessageActionParameters]

    @validator("sections", always=True)
    def sections_may_need_title(cls, v, values):
        if v and len(v) > 1:
            for section in v:
                if not section.title:
                    raise ValueError(
                        "All sections must have a title if there are more than one section"
                    )

        return v


class ListAction(Action):
    button: str
    sections: List[Section]


class ButtonsAction(Action):
    buttons: List[Button]


class FlowAction(Action):
    name: str = "flow"
    parameters: Parameters


class ProductAction(Action):
    catalog_id: str
    product_retailer_id: str


class ProductListAction(Action):
    catalog_id: str
    sections: conlist(ProductSection, min_items=1)


class CatalogMessageAction(Action):
    name: str = "catalog_message"

    @classmethod
    def from_product_retailer_id(cls, product_retailer_id: str):
        return cls(
            parameters=CatalogMessageActionParameters(
                thumbnail_product_retailer_id=product_retailer_id
            )
        )


class Interactive(BaseModel):
    type: InteractiveTypes
    body: Text
    footer: Optional[Text]
    header: Optional[Header]
    action: Union[
        ListAction,
        ButtonsAction,
        FlowAction,
        ProductListAction,
        ProductAction,
        CatalogMessageAction,
    ]

    class Config:
        use_enum_values = True

    @root_validator
    def must_have_header_for_product_list(cls, values):
        if values.get("type") == InteractiveTypes.PRODUCT_LIST and not values.get(
            "header"
        ):
            raise ValueError("Header is required for product list")

        return values


class InteractiveList(Interactive):
    type: InteractiveTypes = InteractiveTypes.LIST
    action: ListAction


class InteractiveButtons(Interactive):
    type: InteractiveTypes = InteractiveTypes.BUTTON
    action: ButtonsAction


class InteractiveFlow(Interactive):
    type: InteractiveTypes = InteractiveTypes.FLOW
    action: FlowAction


class InteractiveProduct(Interactive):
    type: InteractiveTypes = InteractiveTypes.PRODUCT
    header: Literal[None] = None
    action: ProductAction


class InteractiveProductList(Interactive):
    type: InteractiveTypes = InteractiveTypes.PRODUCT_LIST
    header: TextHeader
    action: ProductListAction


class InteractiveCatalogMessage(Interactive):
    type: InteractiveTypes = InteractiveTypes.CATALOG_MESSAGE
    action: CatalogMessageAction
