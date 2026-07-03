import json
from datetime import datetime, timezone
from typing import Optional

import pytest
from aiohttp.client_exceptions import ContentTypeError
from pydantic import BaseModel

from whatsapp import WhatsAppClient, WhatsAppConfig, errors, messages, responses


class TimestampPayload(BaseModel):
    when: datetime
    optional: Optional[str] = None


class FakeResponse:
    def __init__(
        self,
        *,
        status=200,
        reason="OK",
        json_data=None,
        text_data=None,
        json_exception=None,
    ):
        self.status = status
        self.reason = reason
        self._json_data = json_data
        self._text_data = text_data
        self._json_exception = json_exception

    async def json(self):
        if self._json_exception is not None:
            raise self._json_exception
        return self._json_data

    async def text(self):
        if self._text_data is not None:
            return self._text_data
        return json.dumps(self._json_data)

    def raise_for_status(self):
        if self.status >= 400:
            raise AssertionError("raise_for_status should not run when client errors")


class FakeRequestContextManager:
    def __init__(self, response):
        self._response = response

    async def __aenter__(self):
        return self._response

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakeSession:
    def __init__(self, response):
        self.headers = {}
        self.calls = []
        self._response = response

    def request(self, method, url, **kwargs):
        self.calls.append({"method": method, "url": url, "kwargs": kwargs})
        return FakeRequestContextManager(self._response)


def build_client(response):
    config = WhatsAppConfig(
        config_path="/tmp/does-not-exist",
        endpoint="https://example.invalid",
        token="test-token",
    )
    return WhatsAppClient(config=config, session=FakeSession(response))


def make_content_type_error():
    return ContentTypeError(request_info=None, history=(), message="not json")


@pytest.mark.asyncio
async def test_do_request_serializes_base_models_as_json_ready_payloads():
    payload = TimestampPayload(
        when=datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
    )
    client = build_client(FakeResponse(json_data={"success": True, "data": "123456"}))

    response = await client._do_request(
        "POST",
        "https://example.invalid/accounts/code",
        data=payload,
        response_model=responses.PairCodeResponse,
    )

    request = client.session.calls[0]

    assert response.data == "123456"
    assert request["kwargs"]["json"] == payload.model_dump(
        mode="json", exclude_none=True
    )
    assert request["kwargs"]["data"] is None


@pytest.mark.asyncio
async def test_do_request_parses_json_text_bodies_with_model_validate_json():
    client = build_client(
        FakeResponse(
            json_exception=make_content_type_error(),
            text_data='{"success": true, "data": "654321"}',
        )
    )

    response = await client._do_request(
        "GET",
        "https://example.invalid/accounts/code",
        response_model=responses.PairCodeResponse,
    )

    assert isinstance(response, responses.PairCodeResponse)
    assert response.data == "654321"


@pytest.mark.asyncio
async def test_do_request_raises_cloud_api_error_with_serialized_error_payload():
    client = build_client(
        FakeResponse(
            status=400,
            reason="Bad Request",
            json_data={
                "success": False,
                "error": {
                    "message": "Invalid token",
                    "type": "OAuthException",
                    "code": 190,
                    "error_subcode": 123456,
                },
            },
        )
    )

    with pytest.raises(errors.CloudAPIError) as exc_info:
        await client._do_request(
            "POST",
            "https://example.invalid/messages",
            response_model=responses.ApiResponse,
        )

    error = exc_info.value

    assert error.status == 400
    assert error.reason == "Bad Request"
    assert error.message == "Invalid token"
    assert error.error_code == 190
    assert error.data == {
        "message": "Invalid token",
        "type": "OAuthException",
        "code": 190,
        "error_subcode": 123456,
    }


@pytest.mark.asyncio
async def test_send_product_list_accepts_product_section_models(monkeypatch):
    client = build_client(FakeResponse(json_data={"success": True}))
    captured = {}

    async def fake_send(*args, **kwargs):
        captured["data"] = kwargs["data"]
        return kwargs["data"]

    monkeypatch.setattr(client, "send", fake_send)

    message = await client.send_product_list(
        to="15551234567",
        text="Hello",
        header="Products",
        catalog_id="catalog-1",
        product_items=[
            messages.interactive.ProductSection(
                product_items=[
                    messages.interactive.ProductItem(product_retailer_id="sku-1")
                ]
            )
        ],
    )

    assert (
        message.interactive.action.sections[0].product_items[0].product_retailer_id
        == "sku-1"
    )
    assert (
        captured["data"]
        .interactive.action.sections[0]
        .product_items[0]
        .product_retailer_id
        == "sku-1"
    )
