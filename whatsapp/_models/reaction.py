from typing import Optional
from pydantic import BaseModel


class Reaction(BaseModel):
    message_id: str
    emoji: Optional[str] = None
