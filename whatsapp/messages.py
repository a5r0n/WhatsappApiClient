from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, model_validator
from whatsapp._models.contacts import Contact, Contacts
from whatsapp._models.message import MessageType, Text

from whatsapp._models.interactive import (
    InteractiveList,
    InteractiveButtons,
    InteractiveFlow,
    InteractiveProduct,
    InteractiveProductList,
    InteractiveCatalogMessage,
    InteractiveUrl,
    InteractiveContactRequest,
)
from whatsapp._models.reaction import Reaction
from whatsapp._models.template import (
    Template,
    TemplateComponent,
    TemplateParameter,
    TemplateLanguage,
)
from whatsapp._models import interactive, media, message


def _collect_recipient_identifiers(*identifiers: Optional[str]) -> List[str]:
    values: List[str] = []

    for identifier in identifiers:
        if identifier and identifier not in values:
            values.append(identifier)

    return values


def _first_recipient_identifier(*identifiers: Optional[str]) -> Optional[str]:
    return next(iter(_collect_recipient_identifiers(*identifiers)), None)


class AccountInfo(BaseModel):
    webhook_url: Optional[str] = None
    only_status_updates: Optional[bool] = False


class ReadMark(BaseModel):
    messaging_product: str = "whatsapp"
    status: Literal["read"] = "read"
    message_id: str


class Media(BaseModel):
    id: Optional[str] = None
    link: Optional[str] = None
    caption: Optional[str] = None
    filename: Optional[str] = None
    thumbnail: Optional[media.Thumbnail] = None


class Context(BaseModel):
    message_id: str


class Message(BaseModel):
    messaging_product: str = "whatsapp"
    type: MessageType
    to: Optional[str] = None
    recipient: Optional[str] = Field(
        None,
        description=(
            "Business-scoped user ID (BSUID) recipient. "
            "Used when the recipient has no phone-based wa_id."
        ),
    )
    id: Optional[str] = Field(
        None,
        description="The message ID for message to send. available only in unofficial api",
    )
    context: Optional[Context] = None
    text: Optional[Text] = None
    image: Optional[Media] = None
    video: Optional[Media] = None
    audio: Optional[Media] = None
    document: Optional[Media] = None
    contacts: Optional[List[Contact]] = None
    interactive: Optional[  # noqa: F811
        Union[
            InteractiveList,
            InteractiveButtons,
            InteractiveFlow,
            InteractiveProduct,
            InteractiveProductList,
            InteractiveContactRequest,
            InteractiveCatalogMessage,
            InteractiveUrl,
        ]
    ] = None
    template: Optional[Template] = None
    reaction: Optional[Reaction] = None
    recipient_type: Optional[Literal["individual", "group"]] = Field(
        "individual",
        description=(
            "Determines whether the recipient is an individual or a group\n"
            "Specifying recipient_type in the request is optional when the value is individual.\n"
            "However, recipient_type is required when using group."
            " If sending a text message to a group,"
            "see the Sending Group Messages documentation."
        ),
    )
    participants: Optional[List[str]] = Field(
        None,
        description=(
            "The participants array. international format phone numbers."
            "available only in unofficial api"
        ),
    )
    ttl: Optional[Dict[str, Any]] = None
    preview_url: Optional[bool] = Field(
        None,
        description=(
            "Specifying preview_url in the request is optional when not including a URL in your message.\n"
            "To include a URL preview, set preview_url to true in the message body and make sure the URL begins with http:// or https://. "
            "For more information, see the Sending URLs in Text Messages section."
        ),
    )
    model_config = ConfigDict(use_enum_values=True)

    @model_validator(mode="after")
    def validate_recipient(self):
        if not self.recipient_identifiers:
            raise ValueError("One of to or recipient must be specified")

        return self

    @property
    def recipient_identifiers(self) -> List[str]:
        return _collect_recipient_identifiers(self.recipient, self.to)

    @property
    def recipient_identifier(self) -> Optional[str]:
        return _first_recipient_identifier(self.recipient, self.to)
