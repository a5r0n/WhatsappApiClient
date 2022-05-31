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
    response = responses.ApiResponse.parse_obj(messages_offical_response)
    assert isinstance(response.__root__, responses.MessageResponse)

    response = response.__root__
    assert response.success
    assert response.messaging_product == "whatsapp"
    assert response.contacts[0]["wa_id"] == "972543089167"
    assert (
        response.messages[0]["id"]
        == "wamid.HBgMOTcyNTQzMDg5MTY3FQIAERgSMzQyRURGM0E1NkI1ODgzRTE2AA=="
    )
