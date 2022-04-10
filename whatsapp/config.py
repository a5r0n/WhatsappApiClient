from typing import Optional
from . import __version__
from driconfig import DriConfig

from pydantic import BaseModel, BaseSettings, ValidationError, validator
from os.path import split


class ConfigConfig(BaseSettings):
    path: str = "config.yaml"

    class Config:
        env_prefix = "CONFIG_"


class DefaultsConfig(BaseModel):
    preview_url: bool = False


class WhatsAppConfig(DriConfig):
    endpoint: str
    wa_id: Optional[str] = None
    token: Optional[str] = None

    defaults: DefaultsConfig

    use_token: bool = True
    user_agent: str = f"WhatsAppApiClient/{__version__} (python)"

    class Config:
        env_prefix = "WA_"
        config_folder = split(ConfigConfig().path)[0]
        config_file_name = split(ConfigConfig().path)[1]

    @property
    def is_logged_in(self):
        return self.token is not None or (self.wa_id is not None and not self.use_token)
