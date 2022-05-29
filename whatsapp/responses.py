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


class StatusData(BaseModel):
    status: Literal["init", "connected", "error"]
    id: str
    whatsapp_name: Optional[str]
    whatsapp_id: Optional[str]


class UploadedMedia(BaseModel):
    id: str


class Response(BaseModel):
    success: bool
    message: Optional[str]
    data: Optional[Union[dict, list, str, int, bool]]


class LoginResponse(Response):
    data: Account


class LogoutResponse(Response):
    success: Literal[True]
    data: None


class StatusResponse(Response):
    data: Optional[StatusData] = None


class GroupsResponse(Response):
    data: Optional[List[Group]] = []


class UploadResponse(Response):
    media: Optional[List[UploadedMedia]] = []

    @property
    def media_id(self) -> Optional[str]:
        return self.media[0].id if self.media else None
