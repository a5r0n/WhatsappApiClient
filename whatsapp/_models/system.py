from pydantic import BaseModel
from typing import Optional, Literal


class System(BaseModel):
    body: Optional[str] = None
    identity: Optional[str] = None
    new_wa_id: Optional[str] = None
    wa_id: Optional[str] = None
    type: Literal["customer_changed_number", "customer_identity_changed"]
    customer: Optional[str] = None
