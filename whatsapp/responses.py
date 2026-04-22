from datetime import datetime
from typing import Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, RootModel


class Jid(BaseModel):
    user: str
    agent: int
    device: int
    server: int
    ad: bool


class Account(BaseModel):
    id: str
    code: str
    token: str
    image: str


class Privacy(BaseModel):
    type_: Literal["contacts", "blacklist", "whitelist"] = Field(alias="type")
    list_: Optional[List[int]] = Field(None, alias="list")


class Group(BaseModel):
    id: str
    name: str
    topic: Optional[str] = None

    owner: str
    admins: List[str] = []
    members: Optional[List[str]] = []

    created: str
    ephemeral: bool = False
    locked: bool = False


class Newsletter(BaseModel):
    id: str
    name: str
    creation_time: datetime
    description: Optional[str] = None
    profile: Optional[str] = None
    role: Optional[Literal["owner", "admin", "subscriber", "guest"]] = None
    invite: Optional[str] = None
    subscribers: Optional[int] = None
    verified: bool = False
    muted: bool = False


class ContactInfo(BaseModel):
    found: bool = Field(alias="Found")
    first_name: Optional[str] = Field(None, alias="FirstName")
    full_name: Optional[str] = Field(None, alias="FullName")
    push_name: Optional[str] = Field(None, alias="PushName")
    business_name: Optional[str] = Field(None, alias="BusinessName")


class Contact(BaseModel):
    id: int
    info: ContactInfo


class StatusData(BaseModel):
    status: Literal["init", "connected", "error"]
    id: str
    whatsapp_name: Optional[str] = None
    whatsapp_id: Optional[str] = None


class UploadedMedia(BaseModel):
    id: str


class CloudAPIErrorResponse(BaseModel):
    message: str
    type: str
    code: int
    error_subcode: Optional[int] = None
    error_data: Optional[dict] = None


class Response(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Union[dict, list, str, int, bool]] = None
    error: Optional[CloudAPIErrorResponse] = None


class LoginResponse(Response):
    data: Account


class LogoutResponse(Response):
    success: Literal[True]
    data: None


class PrivacyResponse(Response):
    data: Privacy


class StatusResponse(Response):
    data: Optional[StatusData] = None


class GroupsResponse(Response):
    data: Optional[List[Group]] = []


class NewslettersResponse(Response):
    data: Optional[List[Newsletter]] = []


class NewsletterResponse(Response):
    data: Newsletter


class UploadResponse(Response):
    media: List[UploadedMedia]

    @property
    def media_id(self) -> Optional[str]:
        return self.media[0].id if self.media else None


class MessageContact(BaseModel):
    input: str
    wa_id: Optional[str] = None
    user_id: Optional[str] = None
    parent_user_id: Optional[str] = None
    username: Optional[str] = None

    @property
    def identifiers(self) -> List[str]:
        identifiers: List[str] = []

        for value in (self.user_id, self.parent_user_id, self.wa_id, self.input):
            if value and value not in identifiers:
                identifiers.append(value)

        return identifiers

    @property
    def identifier(self) -> str:
        return self.identifiers[0]


class MessageResponse(Response):
    success: bool = True
    messaging_product: Literal["whatsapp"] = "whatsapp"
    contacts: List[Dict[str, str]]
    messages: List[Dict[str, str]]

    @property
    def contact_models(self) -> List[MessageContact]:
        return [MessageContact.model_validate(contact) for contact in self.contacts]


class MediaResponse(Response):
    success: bool = True
    messaging_product: Literal["whatsapp"] = "whatsapp"
    url: str
    mime_type: str
    sha256: str
    file_size: str
    id: str


class ContactsResponse(Response):
    data: List[Contact]


class PairCodeResponse(Response):
    data: str


AnyResponse = Union[
    PrivacyResponse,
    MediaResponse,
    LoginResponse,
    LogoutResponse,
    StatusResponse,
    GroupsResponse,
    NewslettersResponse,
    MessageResponse,
    UploadResponse,
    NewsletterResponse,
    Response,
]


class ApiResponse(RootModel[AnyResponse]):
    pass
