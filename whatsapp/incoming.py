from enum import Enum
from typing import Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field

from whatsapp._models.message import Text
from whatsapp._models.contacts import Contacts


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


class Reply(BaseModel):
    id: str
    title: str
    description: Optional[str]


class Interactive(BaseModel):
    type: Literal["button_reply", "list_reply"]
    button_reply: Optional[Reply] = None
    list_reply: Optional[Reply] = None


class Media(BaseModel):
    id: str
    mime_type: str
    sha256: str
    caption: Optional[str]


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


class Status(BaseModel):
    id: str
    conversation: Optional[Conversation] = None
    pricing: Optional[Pricing] = None
    recipient_id: str
    status: str
    timestamp: str


class Context(BaseModel):
    id: Optional[str] = None
    from_: Optional[str] = Field(None, alias="from")
    forwarded: Optional[bool] = False
    group_id: Optional[str] = None
    mentions: Optional[List[str]] = None


class Button(BaseModel):
    text: str


class Message(BaseModel):
    id: str
    timestamp: str
    from_: str = Field(..., alias="from")
    type: IncomingMessageType
    group_id: Optional[str] = None
    context: Optional[Context]

    text: Optional[Text]
    image: Optional[Media]
    audio: Optional[Media]
    voice: Optional[Media]
    video: Optional[Media]
    document: Optional[Media]
    sticker: Optional[Sticker]
    contacts: Optional[Contacts]
    interactive: Optional[Interactive] = None
    button: Optional[Button]

    class Config:
        use_enum_values = True

    def media(self):
        return self.image or self.audio or self.video or self.voice


class PrivateMessage(Message):
    group_id: Literal["", None]


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


class Updates(BaseModel):
    __root__: Union[StatusUpdate, MessageUpdate]
