import pytest
from pydantic import ValidationError

from whatsapp import WhatsAppClient, WhatsAppConfig, messages


def test_message_supports_phone_number_recipients():
    message = messages.Message(
        to="15551234567",
        type=messages.MessageType.TEXT,
        text=messages.Text(body="hello"),
    )

    assert message.recipient_identifier == "15551234567"
    assert message.recipient_identifiers == ["15551234567"]
    assert message.model_dump(exclude_none=True)["to"] == "15551234567"


def test_message_supports_business_scoped_user_id_recipients():
    message = messages.Message(
        user_id="US.123456789",
        type=messages.MessageType.TEXT,
        text=messages.Text(body="hello"),
    )

    payload = message.model_dump(exclude_none=True)

    assert message.recipient_identifier == "US.123456789"
    assert message.recipient_identifiers == ["US.123456789"]
    assert payload["user_id"] == "US.123456789"
    assert "to" not in payload


def test_message_supports_phone_number_and_business_scoped_user_id_recipients():
    message = messages.Message(
        to="15551234567",
        user_id="US.123456789",
        type=messages.MessageType.TEXT,
        text=messages.Text(body="hello"),
    )

    payload = message.model_dump(exclude_none=True)

    assert message.recipient_identifiers == ["US.123456789", "15551234567"]
    assert payload["to"] == "15551234567"
    assert payload["user_id"] == "US.123456789"


def test_message_supports_parent_business_scoped_user_id_recipients():
    message = messages.Message(
        parent_user_id="US.ENT.123456789",
        type=messages.MessageType.TEXT,
        text=messages.Text(body="hello"),
    )

    payload = message.model_dump(exclude_none=True)

    assert message.recipient_identifier == "US.ENT.123456789"
    assert message.recipient_identifiers == ["US.ENT.123456789"]
    assert payload["parent_user_id"] == "US.ENT.123456789"


def test_interactive_message_serializes_under_pydantic_v2():
    message = messages.Message(
        to="15551234567",
        type=messages.MessageType.INTERACTIVE,
        interactive=messages.interactive.InteractiveButtons(
            body=messages.interactive.Text(text="hello"),
            action=messages.interactive.ButtonsAction(
                buttons=[
                    messages.interactive.Button(
                        reply=messages.interactive.ButtonRow(
                            id="btn-1",
                            title="Hello",
                        )
                    )
                ]
            ),
        ),
    )

    payload = message.model_dump(exclude_none=True)

    assert payload["interactive"]["type"] == "button"
    assert payload["interactive"]["action"]["buttons"][0]["reply"]["id"] == "btn-1"


def test_message_requires_a_recipient_identifier():
    with pytest.raises(ValidationError):
        messages.Message(
            type=messages.MessageType.TEXT,
            text=messages.Text(body="hello"),
        )


def test_message_rejects_user_and_parent_business_scoped_user_ids_together():
    with pytest.raises(ValidationError):
        messages.Message(
            user_id="US.123456789",
            parent_user_id="US.ENT.123456789",
            type=messages.MessageType.TEXT,
            text=messages.Text(body="hello"),
        )


@pytest.mark.asyncio
async def test_client_send_text_supports_business_scoped_user_ids(monkeypatch):
    client = WhatsAppClient(
        WhatsAppConfig(endpoint="https://example.invalid", token="test-token")
    )

    captured = {}

    async def fake_send(*args, **kwargs):
        captured["data"] = kwargs["data"]
        return kwargs["data"]

    monkeypatch.setattr(client, "send", fake_send)

    try:
        message = await client.send_text(text="hello", user_id="US.123456789")
    finally:
        await client.session.close()

    assert message.user_id == "US.123456789"
    assert message.to is None
    assert captured["data"].recipient_identifier == "US.123456789"


@pytest.mark.asyncio
async def test_client_send_media_supports_parent_business_scoped_user_ids(
    monkeypatch,
):
    client = WhatsAppClient(
        WhatsAppConfig(endpoint="https://example.invalid", token="test-token")
    )

    captured = {}

    async def fake_send(*args, **kwargs):
        captured["data"] = kwargs["data"]
        return kwargs["data"]

    monkeypatch.setattr(client, "send", fake_send)

    try:
        message = await client.send_media(
            None,
            type="image",
            media_id="media-123",
            parent_user_id="US.ENT.123456789",
        )
    finally:
        await client.session.close()

    assert message.parent_user_id == "US.ENT.123456789"
    assert message.to is None
    assert captured["data"].recipient_identifier == "US.ENT.123456789"
