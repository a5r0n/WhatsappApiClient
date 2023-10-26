from pydantic import BaseModel
from typing import Optional, Literal


class System(BaseModel):
    body: Optional[str]
    identity: Optional[str]
    new_wa_id: Optional[str]
    wa_id: Optional[str]
    type: Literal["customer_changed_number", "customer_identity_changed"]
    customer: Optional[str]
