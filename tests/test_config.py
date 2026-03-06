import textwrap

from whatsapp import WhatsAppConfig


def write_config(config_path):
    config_path.write_text(
        textwrap.dedent(
            """
            endpoint: https://example.invalid
            wa_id: "1234567890"
            use_token: false
            defaults:
              preview_url: true
            """
        ).strip()
    )


def clear_config_env(monkeypatch):
    for key in [
        "CONFIG_PATH",
        "WA_ENDPOINT",
        "WA_MEDIA_ENDPOINT",
        "WA_WA_ID",
        "WA_TOKEN",
        "WA_USE_TOKEN",
    ]:
        monkeypatch.delenv(key, raising=False)


def assert_loaded_config(config: WhatsAppConfig):
    assert config.endpoint == "https://example.invalid"
    assert config.wa_id == "1234567890"
    assert config.use_token is False
    assert config.defaults.preview_url is True
    assert config.user_agent != ""


def test_whatsapp_config_loads_from_config_path_env(tmp_path, monkeypatch):
    clear_config_env(monkeypatch)
    config_path = tmp_path / "config.yaml"
    write_config(config_path)
    monkeypatch.setenv("CONFIG_PATH", str(config_path))

    config = WhatsAppConfig()

    assert_loaded_config(config)


def test_whatsapp_config_accepts_explicit_config_path(tmp_path, monkeypatch):
    clear_config_env(monkeypatch)
    config_path = tmp_path / "config.yaml"
    write_config(config_path)

    config = WhatsAppConfig(str(config_path))

    assert_loaded_config(config)
