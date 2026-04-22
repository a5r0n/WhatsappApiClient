from whatsapp.incoming import Contact, MessageUpdate, StatusUpdate


def test_message_update_supports_legacy_wa_id_only():
    update = MessageUpdate.model_validate(
        {
            "contacts": [{"profile": {"name": "Legacy User"}, "wa_id": "15551234567"}],
            "messages": [
                {
                    "id": "wamid.legacy",
                    "timestamp": "1713800000",
                    "from": "15551234567",
                    "type": "text",
                    "text": {"body": "hello"},
                }
            ],
        }
    )

    message = update.messages[0]
    contact = Contact.from_update(update, message)

    assert message.from_ == "15551234567"
    assert message.sender_identifier == "15551234567"
    assert message.sender_identifiers == ["15551234567"]
    assert contact.identifier == "15551234567"
    assert contact.as_international == "+15551234567"


def test_message_update_prefers_user_id_matching_over_wa_id():
    update = MessageUpdate.model_validate(
        {
            "contacts": [
                {"profile": {"name": "Legacy Match"}, "wa_id": "15551234567"},
                {
                    "profile": {"name": "Scoped Match"},
                    "wa_id": "16667778888",
                    "user_id": "US.123456789",
                },
            ],
            "messages": [
                {
                    "id": "wamid.scoped",
                    "timestamp": "1713800001",
                    "from": "15551234567",
                    "from_user_id": "US.123456789",
                    "type": "text",
                    "text": {"body": "hello"},
                }
            ],
        }
    )

    message = update.messages[0]
    contact = Contact.from_update(update, message)

    assert message.sender_identifier == "US.123456789"
    assert message.sender_identifiers == ["US.123456789", "15551234567"]
    assert contact.profile.name == "Scoped Match"
    assert contact.identifier == "US.123456789"


def test_message_update_supports_user_id_without_wa_id():
    update = MessageUpdate.model_validate(
        {
            "contacts": [
                {
                    "profile": {"name": "Scoped Only"},
                    "user_id": "US.987654321",
                    "parent_user_id": "US.PARENT.987654321",
                }
            ],
            "messages": [
                {
                    "id": "wamid.user-id-only",
                    "timestamp": "1713800002",
                    "from_user_id": "US.987654321",
                    "from_parent_user_id": "US.PARENT.987654321",
                    "type": "text",
                    "text": {"body": "hello"},
                }
            ],
        }
    )

    message = update.messages[0]
    contact = Contact.from_update(update, message)

    assert message.from_ is None
    assert message.sender_identifier == "US.987654321"
    assert message.sender_identifiers == [
        "US.987654321",
        "US.PARENT.987654321",
    ]
    assert contact.identifier == "US.987654321"
    assert contact.identifiers == ["US.987654321", "US.PARENT.987654321"]
    assert contact.as_international is None


def test_message_update_falls_back_to_wa_id_when_scoped_contact_data_is_missing():
    update = MessageUpdate.model_validate(
        {
            "contacts": [{"profile": {"name": "Legacy User"}, "wa_id": "15551234567"}],
            "messages": [
                {
                    "id": "wamid.fallback",
                    "timestamp": "1713800003",
                    "from": "15551234567",
                    "from_user_id": "US.unknown",
                    "type": "text",
                    "text": {"body": "hello"},
                }
            ],
        }
    )

    contact = Contact.from_update(update, update.messages[0])

    assert contact.profile.name == "Legacy User"
    assert contact.identifier == "15551234567"


def test_status_update_supports_recipient_user_id_without_recipient_id():
    update = StatusUpdate.model_validate(
        {
            "statuses": [
                {
                    "id": "wamid.status",
                    "recipient_user_id": "US.555555555",
                    "recipient_username": "scoped_user",
                    "status": "delivered",
                    "timestamp": "1713800004",
                }
            ]
        }
    )

    status = update.statuses[0]

    assert status.recipient_id is None
    assert status.recipient_user_id == "US.555555555"
    assert status.recipient_username == "scoped_user"
    assert status.recipient_identifier == "US.555555555"
    assert status.recipient_identifiers == ["US.555555555"]
