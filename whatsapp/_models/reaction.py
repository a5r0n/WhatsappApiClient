from typing import Optional
from pydantic import BaseModel, Field


class Reaction(BaseModel):
    message_id: str
    emoji: Optional[str] = Field(None, alias="reaction")
