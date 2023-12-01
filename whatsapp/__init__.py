__version__ = "0.11.2"

from .client import Client as WhatsAppClient
from .config import WhatsAppConfig

__all__ = ["WhatsAppClient", "WhatsAppConfig"]
