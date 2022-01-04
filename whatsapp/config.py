from . import __version__
from driconfig import DriConfig

from pydantic import BaseSettings
from os.path import split


class ConfigConfig(BaseSettings):
    path: str = "config.yaml"

    class Config:
        env_prefix = "CONFIG_"


class WhatsAppConfig(DriConfig):
    wa_id: str
    token: str
    endpoint: str

    use_token: bool = True
    user_agent: str = f"WhatsAppApiClient/{__version__} (python)"

    class Config:
        env_prefix = "WA_"
        config_folder = split(ConfigConfig().path)[0]
        config_file_name = split(ConfigConfig().path)[1]

    @property
    def is_logged_in(self):
        return self.use_token and self.token is not None or self.wa_id is not None
