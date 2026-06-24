import re
from enum import Enum
import json
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import RootModel, field_validator, ConfigDict, BaseModel, Field

from whatsapp._models.message import Text
from whatsapp._models.contacts import Contacts, Location
from whatsapp._models.reaction import Reaction


def _collect_identifiers(*identifiers: Optional[str]) -> List[str]:
    values: List[str] = []

    for identifier in identifiers:
        if identifier and identifier not in values:
            values.append(identifier)

    return values


def _first_identifier(*identifiers: Optional[str]) -> Optional[str]:
    return next(iter(_collect_identifiers(*identifiers)), None)


IDENTIFIER_CHANGE_PATTERN = re.compile(
    r" changed from (?P<previous>\S+) to (?P<current>\S+)$"
)


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
    SYSTEM = "system"
    UNKNOWN = "unknown"
    REACTION = "reaction"
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


class IdentifierChange(BaseModel):
    previous: Optional[str] = None
    current: Optional[str] = None

    @property
    def identifiers(self) -> List[str]:
        return _collect_identifiers(self.previous, self.current)


class Contact(BaseModel):
    profile: Optional[Profile] = None
    wa_id: Optional[str] = None
    user_id: Optional[str] = None
    parent_user_id: Optional[str] = None

    @classmethod
    def from_update(cls, update: "WebhookUpdate", message: BaseModel):
        scoped_contact = next(
            (
                contact
                for contact in update.contacts
                if any(
                    identifier in contact.scoped_user_identifiers
                    for identifier in getattr(
                        message, "sender_scoped_user_identifiers", []
                    )
                )
            ),
            None,
        )
        if scoped_contact is not None:
            return scoped_contact

        return next(
            contact
            for contact in update.contacts
            if any(
                identifier in contact.legacy_identifiers
                for identifier in getattr(message, "sender_legacy_identifiers", [])
            )
        )

    @property
    def scoped_user_identifiers(self) -> List[str]:
        return _collect_identifiers(self.user_id, self.parent_user_id)

    @property
    def legacy_identifiers(self) -> List[str]:
        return _collect_identifiers(self.wa_id)

    @property
    def identifiers(self) -> List[str]:
        return _collect_identifiers(self.user_id, self.parent_user_id, self.wa_id)

    @property
    def identifier(self) -> Optional[str]:
        return _first_identifier(self.user_id, self.parent_user_id, self.wa_id)

    @property
    def as_international(self) -> Optional[str]:
        if self.wa_id is None:
            return None
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
    recipient_user_id: Optional[str] = None
    recipient_username: Optional[str] = None
    message: Optional[StatusMessage] = None
    chat_id: Optional[str] = None
    status: str
    timestamp: str
    errors: Optional[List[StatusError]] = None

    @property
    def recipient_scoped_user_identifiers(self) -> List[str]:
        return _collect_identifiers(self.recipient_user_id)

    @property
    def recipient_legacy_identifiers(self) -> List[str]:
        return _collect_identifiers(self.recipient_id)

    @property
    def recipient_identifiers(self) -> List[str]:
        return _collect_identifiers(self.recipient_user_id, self.recipient_id)

    @property
    def recipient_identifier(self) -> Optional[str]:
        return _first_identifier(self.recipient_user_id, self.recipient_id)


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


class Referral(BaseModel):
    source_type: Optional[str] = None
    source_id: Optional[str] = None
    source_url: Optional[str] = None
    headline: Optional[str] = None
    body: Optional[str] = None
    media_type: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    ctwa_clid: Optional[str] = None


class Button(BaseModel):
    text: str
    payload: Optional[str] = None


class System(BaseModel):
    body: Optional[str] = None
    identity: Optional[str] = None
    new_wa_id: Optional[str] = None
    wa_id: Optional[str] = None
    user_id: Optional[str] = None
    parent_user_id: Optional[str] = None
    customer: Optional[str] = None
    type: str

    def _identifier_change_match(self):
        if not self.body:
            return None
        return IDENTIFIER_CHANGE_PATTERN.search(self.body)

    @property
    def scoped_user_identifiers(self) -> List[str]:
        return _collect_identifiers(self.user_id, self.parent_user_id)

    @property
    def legacy_identifiers(self) -> List[str]:
        return _collect_identifiers(self.wa_id)

    @property
    def identifiers(self) -> List[str]:
        return _collect_identifiers(self.user_id, self.parent_user_id, self.wa_id)

    @property
    def identifier(self) -> Optional[str]:
        return _first_identifier(self.user_id, self.parent_user_id, self.wa_id)

    @property
    def identifier_change(self) -> Optional[IdentifierChange]:
        if self.type != "user_changed_user_id":
            return None

        match = self._identifier_change_match()
        previous = match.group("previous") if match else None
        current_from_body = match.group("current") if match else None

        return IdentifierChange(
            previous=previous,
            current=_first_identifier(self.user_id, self.parent_user_id, current_from_body),
        )


class Message(BaseModel):
    id: str
    timestamp: str
    from_: Optional[str] = Field(None, alias="from")
    from_user_id: Optional[str] = None
    from_parent_user_id: Optional[str] = None
    type: IncomingMessageType
    group_id: Optional[str] = None
    context: Optional[Context] = None
    referral: Optional[Referral] = None

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

    @property
    def sender_scoped_user_identifiers(self) -> List[str]:
        return _collect_identifiers(
            self.from_user_id,
            self.from_parent_user_id,
            self.system.user_id if self.system else None,
            self.system.parent_user_id if self.system else None,
        )

    @property
    def sender_legacy_identifiers(self) -> List[str]:
        return _collect_identifiers(
            self.from_,
            self.system.wa_id if self.system else None,
        )

    @property
    def sender_identifiers(self) -> List[str]:
        return _collect_identifiers(
            self.from_user_id,
            self.from_parent_user_id,
            self.system.user_id if self.system else None,
            self.system.parent_user_id if self.system else None,
            self.from_,
            self.system.wa_id if self.system else None,
        )

    @property
    def sender_identifier(self) -> Optional[str]:
        return _first_identifier(
            self.from_user_id,
            self.from_parent_user_id,
            self.system.user_id if self.system else None,
            self.system.parent_user_id if self.system else None,
            self.from_,
            self.system.wa_id if self.system else None,
        )

    @property
    def identifier_change(self) -> Optional[IdentifierChange]:
        if self.system is None:
            return None
        return self.system.identifier_change


class PrivateMessage(Message):
    group_id: Literal["", None] = None


class GroupMessage(Message):
    group_id: str


class WebhookUpdate(BaseModel):
    messages: Optional[List[Message]] = Field(default_factory=list)
    contacts: Optional[List[Contact]] = Field(default_factory=list)
    statuses: Optional[List[Status]] = Field(default_factory=list)


class MessageUpdate(WebhookUpdate):
    messages: List[Union[PrivateMessage, GroupMessage]]
    contacts: List[Contact] = Field(default_factory=list)


class StatusUpdate(WebhookUpdate):
    statuses: List[Status]


class UserIdUpdate(BaseModel):
    detail: str
    timestamp: str
    wa_id: Optional[str] = None
    user_id: IdentifierChange
    parent_user_id: Optional[IdentifierChange] = None

    @property
    def legacy_identifiers(self) -> List[str]:
        return _collect_identifiers(self.wa_id)

    @property
    def previous_scoped_user_identifiers(self) -> List[str]:
        return _collect_identifiers(
            self.user_id.previous,
            self.parent_user_id.previous if self.parent_user_id else None,
        )

    @property
    def current_scoped_user_identifiers(self) -> List[str]:
        return _collect_identifiers(
            self.user_id.current,
            self.parent_user_id.current if self.parent_user_id else None,
        )

    @property
    def previous_identifier(self) -> Optional[str]:
        return _first_identifier(
            self.user_id.previous,
            self.parent_user_id.previous if self.parent_user_id else None,
        )

    @property
    def current_identifier(self) -> Optional[str]:
        return _first_identifier(
            self.user_id.current,
            self.parent_user_id.current if self.parent_user_id else None,
            self.wa_id,
        )

    @property
    def identifier_change(self) -> IdentifierChange:
        return self.user_id


class UserIdUpdateWebhookUpdate(BaseModel):
    contacts: Optional[List[Contact]] = Field(default_factory=list)
    user_id_update: UserIdUpdate

    @property
    def identifier_change(self) -> IdentifierChange:
        return self.user_id_update.identifier_change


class Updates(RootModel[Union[StatusUpdate, MessageUpdate, UserIdUpdateWebhookUpdate]]):
    pass
