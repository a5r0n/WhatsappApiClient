from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
import uuid

from pydantic import (
    StringConstraints,
    ConfigDict,
    BaseModel,
    Field,
    field_validator,
    model_validator,
)
from .media import Media
from typing_extensions import Annotated


def _as_dict(values):
    if isinstance(values, BaseModel):
        return values.model_dump(exclude_none=True)
    return values


class InteractiveTypes(str, Enum):
    LIST = "list"
    URL = "cta_url"
    BUTTON = "button"
    PRODUCT = "product"
    PRODUCT_LIST = "product_list"
    FLOW = "flow"
    CATALOG_MESSAGE = "catalog_message"
    CONTACT_REQUEST = "contact_request"


class HeaderTypes(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"


class Text(BaseModel):
    text: str


class Header(BaseModel):
    type: HeaderTypes
    text: Optional[Union[Text, str]] = None
    video: Optional[Media] = None
    image: Optional[Media] = None
    document: Optional[Media] = None


class TextHeader(Header):
    type: Literal[HeaderTypes.TEXT] = HeaderTypes.TEXT
    text: str


class Row(BaseModel):
    id: str
    title: str


class ButtonRow(Row):
    title: Annotated[str, StringConstraints(max_length=20)]


class SectionRow(Row):
    title: Annotated[str, StringConstraints(max_length=23)]
    description: Optional[Annotated[str, StringConstraints(max_length=72)]] = None


class ProductItem(BaseModel):
    product_retailer_id: str


class Button(BaseModel):
    type: str = "reply"
    reply: ButtonRow


class Section(BaseModel):
    title: Optional[str] = None
    rows: Optional[List[SectionRow]] = None
    product_items: Optional[List[ProductItem]] = None


class ListSection(Section):
    rows: List[SectionRow]


class FlowParametersPayload(BaseModel):
    screen: str
    data: Optional[Dict[str, Any]] = None


class FlowParameters(BaseModel):
    mode: Literal["draft", "published"]
    flow_message_version: int = 3
    flow_token: str = Field(
        description="A unique token that identifies the flow message.",
        default_factory=lambda: str(uuid.uuid4()),
    )
    flow_id: str
    flow_cta: str
    flow_action: Literal["navigate", "data_exchange"]
    flow_action_payload: Optional[FlowParametersPayload] = None

    @model_validator(mode="before")
    def validate_payload_when_action_is_navigate(cls, values):
        values = _as_dict(values)
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


class UrlParameters(BaseModel):
    display_text: str
    url: str


class Action(BaseModel):
    name: Optional[str] = None
    button: Optional[Button] = None
    buttons: Optional[List[Button]] = None
    sections: Optional[List[Section]] = None
    parameters: Optional[
        Union[FlowParameters, CatalogMessageActionParameters, UrlParameters]
    ] = None
    catalog_id: Optional[str] = None
    product_retailer_id: Optional[str] = None

    @field_validator("sections")
    @classmethod
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
    parameters: FlowParameters


class ProductAction(Action):
    catalog_id: str
    product_retailer_id: str


class ProductListAction(Action):
    catalog_id: str
    sections: Annotated[List[ProductSection], Field(min_length=1)]


class CatalogMessageAction(Action):
    name: str = "catalog_message"

    @classmethod
    def from_product_retailer_id(cls, product_retailer_id: str):
        return cls(
            parameters=CatalogMessageActionParameters(
                thumbnail_product_retailer_id=product_retailer_id
            )
        )


class UrlAction(Action):
    name: Literal["cta_url"] = "cta_url"
    parameters: UrlParameters

    @classmethod
    def from_url(cls, url: str, display_text: str):
        return cls(parameters=UrlParameters(url=url, display_text=display_text))


class ContactRequestAction(Action):
    name: Literal["request_contact_info"] = "request_contact_info"


class Interactive(BaseModel):
    type: InteractiveTypes
    body: Text
    footer: Optional[Text] = None
    header: Optional[Header] = None
    action: Union[
        ListAction,
        ButtonsAction,
        FlowAction,
        ProductListAction,
        ProductAction,
        ContactRequestAction,
        CatalogMessageAction,
        UrlAction,
    ]
    model_config = ConfigDict(use_enum_values=True)

    @model_validator(mode="before")
    def must_have_header_for_product_list(cls, values):
        values = _as_dict(values)
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


class InteractiveUrl(Interactive):
    type: InteractiveTypes = InteractiveTypes.URL
    action: UrlAction


class InteractiveContactRequest(Interactive):
    type: InteractiveTypes = InteractiveTypes.CONTACT_REQUEST
    header: Literal[None] = None
    footer: Literal[None] = None
    action: ContactRequestAction
