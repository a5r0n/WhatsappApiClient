import pytest

from whatsapp import responses


@pytest.fixture
def messages_offical_response():
    return {
        "messaging_product": "whatsapp",
        "contacts": [{"input": "972543089167", "wa_id": "972543089167"}],
        "messages": [
            {"id": "wamid.HBgMOTcyNTQzMDg5MTY3FQIAERgSMzQyRURGM0E1NkI1ODgzRTE2AA=="}
        ],
    }


def test_messages_response(messages_offical_response):
    response = responses.ApiResponse.model_validate(messages_offical_response)
    assert isinstance(response.root, responses.MessageResponse)

    response = response.root
    assert response.success
    assert response.messaging_product == "whatsapp"
    assert response.contacts[0]["wa_id"] == "972543089167"
    assert response.contact_models[0].identifier == "972543089167"
    assert (
        response.messages[0]["id"]
        == "wamid.HBgMOTcyNTQzMDg5MTY3FQIAERgSMzQyRURGM0E1NkI1ODgzRTE2AA=="
    )


def test_messages_response_supports_business_scoped_user_ids():
    response = responses.ApiResponse.model_validate(
        {
            "messaging_product": "whatsapp",
            "contacts": [
                {
                    "input": "US.123456789",
                    "user_id": "US.123456789",
                    "parent_user_id": "US.ENT.123456789",
                    "username": "scoped_user",
                }
            ],
            "messages": [{"id": "wamid.scoped"}],
        }
    ).root

    assert isinstance(response, responses.MessageResponse)
    assert response.contacts[0]["user_id"] == "US.123456789"
    assert response.contact_models[0].parent_user_id == "US.ENT.123456789"
    assert response.contact_models[0].username == "scoped_user"
    assert response.contact_models[0].identifier == "US.123456789"


def test_media_response_accepts_graph_api_integer_file_size():
    response = responses.MediaResponse.model_validate(
        {
            "id": "974888005314047",
            "messaging_product": "whatsapp",
            "url": "https://lookaside.fbsbx.com/whatsapp_business/attachments/974888005314047",
            "mime_type": "image/jpeg",
            "sha256": "088bae189dedac6c9c91286c31eb5df50a08da452f246a75802ba1ce6252d6d7",
            "file_size": 85175,
        }
    )

    assert response.file_size == 85175


def test_media_response_accepts_legacy_string_file_size():
    response = responses.MediaResponse.model_validate(
        {
            "id": "974888005314047",
            "messaging_product": "whatsapp",
            "url": "https://lookaside.fbsbx.com/whatsapp_business/attachments/974888005314047",
            "mime_type": "image/jpeg",
            "sha256": "088bae189dedac6c9c91286c31eb5df50a08da452f246a75802ba1ce6252d6d7",
            "file_size": "85175",
        }
    )

    assert response.file_size == 85175


def test_api_response_detects_media_response_with_integer_file_size():
    response = responses.ApiResponse.model_validate(
        {
            "id": "974888005314047",
            "messaging_product": "whatsapp",
            "url": "https://lookaside.fbsbx.com/whatsapp_business/attachments/974888005314047",
            "mime_type": "image/jpeg",
            "sha256": "088bae189dedac6c9c91286c31eb5df50a08da452f246a75802ba1ce6252d6d7",
            "file_size": 85175,
        }
    ).root

    assert isinstance(response, responses.MediaResponse)
    assert response.file_size == 85175
