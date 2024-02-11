from enum import Enum
import json
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import RootModel, field_validator, ConfigDict, BaseModel, Field

from whatsapp._models.message import Text
from whatsapp._models.contacts import Contacts, Location
from whatsapp._models.reaction import Reaction
from whatsapp._models.system import System


class IncomingMessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    VOICE = "voice"
    DOCUMENT = "document"
    LOCATION = "location"
    STICKER = "sticker"
    CONTACTS = "contacts"
    HSM = "hsm"
    INTERACTIVE = "interactive"
    BUTTON = "button"
    UNKNOWN = "unknown"
    REACTION = "reaction"
    SYSTEM = "system"
    ORDER = "order"
    REQUEST_WELCOME = "request_welcome"


class Reply(BaseModel):
    id: str
    title: str
    description: Optional[str] = None


class FlowReplay(BaseModel):
    name: str
    response_json: Dict[str, Any]

    @field_validator("response_json", mode="before")
    @classmethod
    def convert_json(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v


class Interactive(BaseModel):
    type: Literal["button_reply", "list_reply", "nfm_reply"]
    button_reply: Optional[Reply] = None
    list_reply: Optional[Reply] = None
    nfm_reply: Optional[FlowReplay] = None


class OrderProductItem(BaseModel):
    product_retailer_id: str
    quantity: Union[float, str]
    item_price: Union[float, str]
    currency: str


class Order(BaseModel):
    catalog_id: str
    text: Optional[str] = None
    product_items: List[OrderProductItem]


class Media(BaseModel):
    id: str
    mime_type: str
    sha256: str
    caption: Optional[str] = None


class Sticker(Media):
    metadata: Dict[str, Union[str, int, List[str]]]


class Profile(BaseModel):
    name: str


class Contact(BaseModel):
    profile: Profile
    wa_id: str

    @classmethod
    def from_update(cls, update: "WebhookUpdate", message: BaseModel):
        return next(
            filter(lambda contact: contact.wa_id == message.from_, update.contacts)
        )

    @property
    def as_international(self):
        return f"+{self.wa_id}"


class Conversation(BaseModel):
    id: str


class Pricing(BaseModel):
    billable: bool
    pricing_model: str


class StatusError(BaseModel):
    code: int
    title: Optional[str] = None


class StatusMessage(BaseModel):
    recipient_id: Optional[str] = None
    group_id: Optional[str] = None


class Status(BaseModel):
    id: str
    conversation: Optional[Conversation] = None
    pricing: Optional[Pricing] = None
    recipient_id: Optional[str] = None
    message: Optional[StatusMessage] = None
    chat_id: Optional[str] = None
    status: str
    timestamp: str
    errors: Optional[List[StatusError]] = None


class ReferredProduct(BaseModel):
    catalog_id: str
    product_retailer_id: str


class Context(BaseModel):
    id: Optional[str] = None
    from_: Optional[str] = Field(None, alias="from")
    referred_product: Optional[ReferredProduct] = None
    forwarded: Optional[bool] = False
    group_id: Optional[str] = None
    mentions: Optional[List[str]] = None


class Button(BaseModel):
    text: str
    payload: Optional[str] = None


class Message(BaseModel):
    id: str
    timestamp: str
    from_: str = Field(..., alias="from")
    type: IncomingMessageType
    group_id: Optional[str] = None
    context: Optional[Context] = None

    text: Optional[Text] = None
    image: Optional[Media] = None
    audio: Optional[Media] = None
    voice: Optional[Media] = None
    video: Optional[Media] = None
    document: Optional[Media] = None
    sticker: Optional[Sticker] = None
    contacts: Optional[Contacts] = None
    interactive: Optional[Interactive] = None
    button: Optional[Button] = None
    location: Optional[Location] = None
    reaction: Optional[Reaction] = None
    system: Optional[System] = None
    order: Optional[Order] = None
    model_config = ConfigDict(use_enum_values=True)

    def media(self):
        return self.image or self.audio or self.video or self.voice


class PrivateMessage(Message):
    group_id: Literal["", None] = None


class GroupMessage(Message):
    group_id: str


class WebhookUpdate(BaseModel):
    messages: Optional[List[Message]] = []
    contacts: Optional[List[Contact]] = []
    statuses: Optional[List[Status]] = []


class MessageUpdate(WebhookUpdate):
    messages: List[Union[PrivateMessage, GroupMessage]]
    contacts: List[Contact]


class StatusUpdate(WebhookUpdate):
    statuses: List[Status]


class Updates(RootModel[Union[StatusUpdate, MessageUpdate]]):
    root: Union[StatusUpdate, MessageUpdate]

    @property
    def __root__(self):
        return self.root
