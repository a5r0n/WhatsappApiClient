from contextvars import ContextVar
from typing import Any, Dict, Optional, Tuple, Type
from . import __version__
import yaml
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource


class ConfigConfig(BaseSettings):
    path: str = "config.yaml"
    model_config = SettingsConfigDict(env_prefix="CONFIG_")


class DefaultsConfig(BaseModel):
    preview_url: bool = False


_config_path_override: ContextVar[Optional[str]] = ContextVar(
    "config_path_override", default=None
)


class YamlConfigSource(PydanticBaseSettingsSource):
    def __init__(self, settings_cls: Type[BaseSettings], yaml_file: str):
        super().__init__(settings_cls)
        self.yaml_file = yaml_file

    def get_field_value(self, field: Any, field_name: str) -> Tuple[Any, str, bool]:
        return None, field_name, False

    def __call__(self) -> Dict[str, Any]:
        try:
            with open(self.yaml_file) as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}


class WhatsAppConfig(BaseSettings):
    endpoint: str
    media_endpoint: Optional[str] = None
    wa_id: Optional[str] = None
    token: Optional[str] = None

    defaults: Optional[DefaultsConfig] = Field(default_factory=DefaultsConfig)

    use_token: bool = True
    user_agent: str = f"WhatsAppApiClient/{__version__} (python)"

    model_config = SettingsConfigDict(env_prefix="WA_")

    def __init__(self, config_path: Optional[str] = None, **values):
        token = _config_path_override.set(config_path)
        try:
            super().__init__(**values)
        finally:
            _config_path_override.reset(token)

    @field_validator("wa_id", mode="before")
    @classmethod
    def coerce_wa_id_to_string(cls, value):
        if value is None:
            return value
        return str(value)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        config_path = _config_path_override.get() or ConfigConfig().path
        return (
            env_settings,
            YamlConfigSource(settings_cls, config_path),
            init_settings,
        )

    @property
    def is_logged_in(self):
        return self.token is not None or (self.wa_id is not None and not self.use_token)
