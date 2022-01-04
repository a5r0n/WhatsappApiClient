from typing import Optional
from pydantic import BaseModel


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
    jid: Jid


class Response(BaseModel):
    success: bool
    message: Optional[str]
    data: Optional[dict]


class LoginResponse(Response):
    data: Account
