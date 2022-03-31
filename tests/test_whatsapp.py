import asyncio
import mimetypes
from typing import List, Tuple

import aiohttp
from whatsapp import __version__
import pytest
from whatsapp import WhatsAppClient, WhatsAppConfig

import os


def test_whatsapp_config(whatsapp_config):
    assert whatsapp_config.use_token == False
    assert whatsapp_config.wa_id != ""
    assert whatsapp_config.user_agent != ""


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="session")
def config_path() -> str:
    return os.path.join(os.path.dirname(__file__), "..", ".config.yaml")


@pytest.fixture(scope="session")
def whatsapp_config(config_path):
    return WhatsAppConfig(config_path)


@pytest.fixture
def logged_out_whatsapp_config(config_path):
    c = WhatsAppConfig(config_path)
    c.use_token = True
    return c


@pytest.fixture
async def logged_out_client(logged_out_whatsapp_config):
    client = WhatsAppClient(logged_out_whatsapp_config)
    async with client:
        yield client


@pytest.fixture(scope="session")
async def client(whatsapp_config):
    client = WhatsAppClient(whatsapp_config)
    async with client:
        yield client


@pytest.fixture(scope="session")
def to(whatsapp_config):
    return os.getenv("WHATSAPP_TO", whatsapp_config.wa_id)


@pytest.fixture(scope="session")
def text():
    return "Hello World!"


@pytest.fixture(scope="session")
def buttons():
    return [("1", "Button 1"), ("2", "Button 2")]


@pytest.fixture(scope="session")
def list_title():
    return "List Title"


@pytest.fixture(scope="session")
def list_buttons():
    return [("1", "Button 1"), ("2", "Button 2")]


@pytest.fixture(scope="session")
def base_path():
    return os.path.join(os.path.dirname(__file__), "files")


@pytest.fixture(scope="session")
def image_path(base_path):
    return os.path.join(base_path, "image.jpg")


@pytest.fixture(scope="session")
def image_url():
    return "https://filesamples.com/samples/image/jpeg/sample_640%C3%97426.jpeg"


@pytest.fixture(scope="session")
def document_path(base_path):
    return os.path.join(base_path, "test.pdf")


@pytest.fixture(scope="session")
def document_url():
    return "https://filesamples.com/samples/document/pdf/sample1.pdf"


@pytest.fixture(scope="session")
def audio_path(base_path):
    return os.path.join(base_path, "audio.mp3")


@pytest.fixture(scope="session")
def audio_url():
    return "https://filesamples.com/samples/audio/mp3/sample1.mp3"


@pytest.fixture(scope="session")
def video_path(base_path):
    return os.path.join(base_path, "video.mp4")


@pytest.fixture(scope="session")
def video_url():
    return "https://filesamples.com/samples/video/mp4/sample_640x360.mp4"


@pytest.fixture(scope="module")
async def image_media(client: WhatsAppClient, image_path: str):
    return await upload_media(client, image_path)


@pytest.fixture(scope="session")
async def document_media(client: WhatsAppClient, document_path: str):
    return await upload_media(client, document_path)


@pytest.fixture(scope="session")
async def audio_media(client: WhatsAppClient, audio_path: str):
    return await upload_media(client, audio_path)


@pytest.fixture(scope="session")
async def video_media(client: WhatsAppClient, video_path: str):
    return await upload_media(client, video_path)


@pytest.fixture
async def aiohttp_client():
    async with aiohttp.ClientSession() as session:
        yield session


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "file_url", ["image_url", "video_url", "audio_url", "document_url"]
)
async def test_urls_are_valid(file_url, aiohttp_client, request):
    url = request.getfixturevalue(file_url)
    async with aiohttp_client.head(url) as response:
        assert response.status == 200


@pytest.mark.asyncio
async def test_login(logged_out_client: WhatsAppClient):
    assert logged_out_client.config.token is None
    assert not logged_out_client.config.is_logged_in
    assert await logged_out_client.login()


@pytest.mark.asyncio
async def test_send_message(client: WhatsAppClient, to: str, text: str):
    await client.send_text(to, text)


@pytest.mark.asyncio
async def test_send_buttons(
    client: WhatsAppClient, to: str, text: str, buttons: List[Tuple[str, str]]
):
    await client.send_buttons(to, text, buttons)


@pytest.mark.asyncio
async def test_send_list(
    client: WhatsAppClient,
    to: str,
    text: str,
    list_title: str,
    list_buttons: List[Tuple[str, str]],
):
    await client.send_list(to, text, list_title, list_buttons)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "file_path", ["image_path", "video_path", "audio_path", "document_path"]
)
async def test_upload_media(client: WhatsAppClient, file_path: str, request):
    file_path = request.getfixturevalue(file_path)
    media_resp = await upload_media(client, file_path)


async def upload_media(client: WhatsAppClient, file_path: str):
    with open(file_path, "rb") as f:
        media_resp = await client.upload(f.read(), mimetypes.guess_type(file_path)[0])

    media_id = media_resp.media.pop().id
    assert media_id is not None
    return media_id


@pytest.mark.asyncio
@pytest.mark.parametrize("caption", ["With Caption", "", None, "With\nNew\nLines"])
async def test_send_image_local(
    client: WhatsAppClient, to: str, image_media: str, caption, request
):
    await client.send_image(to, media_id=image_media, caption=caption)


@pytest.mark.asyncio
async def test_send_image_url(client: WhatsAppClient, to: str, image_url: str, caption):
    resp = await client.send_image(to, media_link=image_url, caption=caption)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "filename", ["With Filename.pdf", "", None, "With\nNew\nLines.pdf"]
)
async def test_send_document_local(
    client: WhatsAppClient, to: str, document_media: str, filename
):

    await client.send_document(
        to, media_id=document_media, filename=filename, caption="Test"
    )


@pytest.mark.asyncio
async def test_send_document_url(
    client: WhatsAppClient, to: str, document_url: str, filename
):
    resp = await client.send_document(
        to, media_link=document_url, filename=filename, caption="Test"
    )


@pytest.mark.asyncio
async def test_send_audio_local(client: WhatsAppClient, to: str, audio_path: str):
    media_id = await upload_media(client, audio_path)
    await client.send_audio(to, media_id=media_id)


@pytest.mark.asyncio
async def test_send_audio_url(client: WhatsAppClient, to: str, audio_url: str):
    resp = await client.send_audio(to, media_link=audio_url)


@pytest.mark.asyncio
@pytest.mark.parametrize("caption", ["With Caption", "", None, "With\nNew\nLines"])
async def test_send_video_local(
    client: WhatsAppClient, to: str, video_media: str, caption: str
):
    await client.send_video(to, media_id=video_media, caption=caption)


@pytest.mark.asyncio
async def test_send_video_url(
    client: WhatsAppClient, to: str, video_url: str, caption: str
):
    resp = await client.send_video(to, media_link=video_url, caption=caption)
