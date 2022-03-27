from typing import Dict, List, Literal, Optional
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


class Participant(BaseModel):
    is_admin: bool = Field(..., alias="IsAdmin")
    is_super_admin: bool = Field(..., alias="IsSuperAdmin")
    jid: str = Field(..., alias="JID")


class Group(BaseModel):
    announce_version_id: str = Field(None, alias="AnnounceVersionID")
    jid: str = Field(None, alias="JID")
    name: str = Field(None, alias="Name")
    name_set_at: str = Field(None, alias="NameSetAt")
    name_set_by: str = Field(None, alias="NameSetBy")
    owner_jid: str = Field(None, alias="OwnerJID")

    participant_version_id: str = Field(None, alias="ParticipantVersionID")
    participants: Optional[List[Participant]] = Field(None, alias="Participants")

    disappearing_timer: Optional[int] = Field(None, alias="DisappearingTimer")
    group_created: Optional[str] = Field(None, alias="GroupCreated")

    is_announce: bool = Field(None, alias="IsAnnounce")
    is_ephemeral: bool = Field(None, alias="IsEphemeral")
    is_locked: bool = Field(None, alias="IsLocked")

    topic: Optional[str] = Field(None, alias="Topic")
    topic_id: Optional[str] = Field(None, alias="TopicID")
    topic_set_at: Optional[str] = Field(None, alias="TopicSetAt")
    topic_set_by: Optional[str] = Field(None, alias="TopicSetBy")


class AccountStatus(BaseModel):
    id: str
    jid: str
    webhook_url: Optional[str]
    whatsapp_name: Optional[str]
    whatsapp_id: int
    status: Literal["init", "connected", "error"]


class UploadedMedia(BaseModel):
    id: str


class Response(BaseModel):
    success: bool
    message: Optional[str]
    data: Optional[dict]


class LoginResponse(Response):
    data: Account


class StatusResponse(Response):
    data: Optional[Dict] = {}


class GroupsResponse(Response):
    data: Optional[List[Group]] = []


class UploadResponse(Response):
    media: Optional[List[UploadedMedia]] = []
