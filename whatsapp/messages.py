from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field
from whatsapp._models.contacts import Contact, Contacts
from whatsapp._models.message import MessageType, Text

from whatsapp._models.interactive import (
    InteractiveList,
    InteractiveButtons,
    InteractiveFlow,
)
from whatsapp._models.reaction import Reaction
from whatsapp._models.template import (
    Template,
    TemplateComponent,
    TemplateParameter,
    TemplateLanguage,
)
from whatsapp._models import interactive, media, message


class AccountInfo(BaseModel):
    webhook_url: Optional[str]
    only_status_updates: Optional[bool] = False


class ReadMark(BaseModel):
    messaging_product: str = "whatsapp"
    status: Literal["read"] = "read"
    message_id: str


class Media(BaseModel):
    id: Optional[str]
    link: Optional[str]
    caption: Optional[str]
    filename: Optional[str]
    thumbnail: Optional[media.Thumbnail]


class Context(BaseModel):
    message_id: str


class Message(BaseModel):
    messaging_product: str = "whatsapp"
    type: MessageType
    to: str
    context: Optional[Context]
    text: Optional[Text]
    image: Optional[Media]
    video: Optional[Media]
    audio: Optional[Media]
    document: Optional[Media]
    contacts: Optional[List[Contact]]
    interactive: Optional[Union[InteractiveList, InteractiveButtons, InteractiveFlow]]
    template: Optional[Template]
    reaction: Optional[Reaction]
    recipient_type: Optional[Literal["individual", "group"]] = Field(
        "individual",
        description="Determines whether the recipient is an individual or a group\nSpecifying recipient_type in the request is optional when the value is individual.\nHowever, recipient_type is required when using group. If sending a text message to a group, see the Sending Group Messages documentation.",
    )
    ttl: Optional[Dict[str, Any]] = None
    preview_url: Optional[bool] = Field(
        None,
        description="Specifying preview_url in the request is optional when not including a URL in your message.\nTo include a URL preview, set preview_url to true in the message body and make sure the URL begins with http:// or https://. For more information, see the Sending URLs in Text Messages section.",
    )

    class Config:
        use_enum_values = True
