from datetime import datetime
from typing import Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


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
    topic: Optional[str]

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
    description: Optional[str]
    profile: Optional[str]
    role: Optional[Literal["owner", "admin", "subscriber", "guest"]]
    invite: Optional[str]
    subscribers: Optional[int]
    verified: bool = False
    muted: bool = False


class ContactInfo(BaseModel):
    found: bool = Field(alias="Found")
    first_name: Optional[str] = Field(alias="FirstName")
    full_name: Optional[str] = Field(alias="FullName")
    push_name: Optional[str] = Field(alias="PushName")
    business_name: Optional[str] = Field(alias="BusinessName")


class Contact(BaseModel):
    id: int
    info: ContactInfo


class StatusData(BaseModel):
    status: Literal["init", "connected", "error"]
    id: str
    whatsapp_name: Optional[str]
    whatsapp_id: Optional[str]


class UploadedMedia(BaseModel):
    id: str


class CloudAPIErrorResponse(BaseModel):
    message: str
    type: str
    code: int
    error_subcode: Optional[int]
    error_data: Optional[dict]


class Response(BaseModel):
    success: bool
    message: Optional[str]
    data: Optional[Union[dict, list, str, int, bool]]
    error: Optional[CloudAPIErrorResponse]


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


class MessageResponse(Response):
    success: bool = True
    messaging_product: Literal["whatsapp"] = "whatsapp"
    contacts: List[Dict[str, str]]
    messages: List[Dict[str, str]]


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


class ApiResponse(BaseModel):
    __root__: AnyResponse
