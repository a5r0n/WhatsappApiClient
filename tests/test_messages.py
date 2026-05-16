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
        recipient="US.123456789",
        type=messages.MessageType.TEXT,
        text=messages.Text(body="hello"),
    )

    payload = message.model_dump(exclude_none=True)

    assert message.recipient_identifier == "US.123456789"
    assert message.recipient_identifiers == ["US.123456789"]
    assert payload["recipient"] == "US.123456789"
    assert "to" not in payload


def test_message_supports_phone_number_and_business_scoped_user_id_recipients():
    message = messages.Message(
        to="15551234567",
        recipient="US.123456789",
        type=messages.MessageType.TEXT,
        text=messages.Text(body="hello"),
    )

    payload = message.model_dump(exclude_none=True)

    assert message.recipient_identifiers == ["US.123456789", "15551234567"]
    assert payload["to"] == "15551234567"
    assert payload["recipient"] == "US.123456789"


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
        message = await client.send_text(text="hello", recipient="US.123456789")
    finally:
        await client.session.close()

    assert message.recipient == "US.123456789"
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
            recipient="US.ENT.123456789",
        )
    finally:
        await client.session.close()

    assert message.recipient == "US.ENT.123456789"
    assert message.to is None
    assert captured["data"].recipient_identifier == "US.ENT.123456789"


def test_interactive_contact_request_serializes_to_meta_shape():
    message = messages.Message(
        recipient="US.123456789",
        type=messages.MessageType.INTERACTIVE,
        interactive=messages.interactive.InteractiveContactRequest(
            body=messages.interactive.Text(text="Share your number with us"),
            action=messages.interactive.ContactRequestAction(),
        ),
    )

    payload = message.model_dump(exclude_none=True)

    assert payload["interactive"]["type"] == "request_contact_info"
    assert payload["interactive"]["body"] == {"text": "Share your number with us"}
    assert payload["interactive"]["action"] == {"name": "request_contact_info"}
    assert "header" not in payload["interactive"]
    assert "footer" not in payload["interactive"]
    assert payload["recipient"] == "US.123456789"


def test_interactive_contact_request_action_name_is_fixed():
    with pytest.raises(ValidationError):
        messages.interactive.ContactRequestAction(name="something_else")


def test_message_validates_contact_request_via_interactive_union():
    payload = {
        "recipient": "US.123456789",
        "type": "interactive",
        "interactive": {
            "type": "request_contact_info",
            "body": {"text": "Share your number with us"},
            "action": {"name": "request_contact_info"},
        },
    }

    message = messages.Message.model_validate(payload)

    assert isinstance(
        message.interactive, messages.interactive.InteractiveContactRequest
    )


def test_contact_request_action_resolves_to_correct_type_in_union():
    from whatsapp._models import interactive

    parsed = interactive.Interactive.model_validate(
        {
            "type": "request_contact_info",
            "body": {"text": "hi"},
            "action": {"name": "request_contact_info"},
        }
    )

    assert isinstance(parsed.action, interactive.ContactRequestAction)
