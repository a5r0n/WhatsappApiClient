import mimetypes
from typing import List, Tuple
from whatsapp import __version__
import pytest
from whatsapp import WhatsAppClient, WhatsAppConfig

import os


def test_version():
    assert __version__ == "0.1.3"


@pytest.fixture
async def client():
    wa_id = os.getenv("WHATSAPP_ID")
    endpoint = os.getenv("WHATSAPP_ENDPOINT")
    client = WhatsAppClient(WhatsAppConfig(wa_id=wa_id, endpoint=endpoint))
    async with client:
        yield client


@pytest.fixture
def to():
    return os.getenv("WHATSAPP_TO")


@pytest.fixture
def text():
    return "Hello World!"


@pytest.fixture
def buttons():
    return [("1", "Button 1"), ("2", "Button 2")]


@pytest.fixture
def list_title():
    return "List Title"


@pytest.fixture
def list_buttons():
    return [("1", "Button 1"), ("2", "Button 2")]


@pytest.fixture
def image_path():
    return os.path.join(os.path.dirname(__file__), "image.jpg")


@pytest.fixture
def image_url():
    return "https://i.picsum.photos/id/237/200/300.jpg?hmac=TmmQSbShHz9CdQm0NkEjx1Dyh_Y984R9LpNrpvH2D_U"


@pytest.fixture
def document_path():
    return os.path.join(os.path.dirname(__file__), "test.pdf")


@pytest.fixture
def document_url():
    return "https://s2.q4cdn.com/498544986/files/doc_downloads/test.pdf"


@pytest.fixture
def audio_path():
    return os.path.join(os.path.dirname(__file__), "audio.mp3")


@pytest.fixture
def audio_url():
    return "https://file-examples.com/storage/fe07f859fd624073f9dbdc6/2017/11/file_example_MP3_700KB.mp3"


@pytest.fixture
def video_path():
    return os.path.join(os.path.dirname(__file__), "video.mp4")


@pytest.fixture
def video_url():
    return "https://file-examples.com/storage/fe07f859fd624073f9dbdc6/2017/04/file_example_MP4_480_1_5MG.mp4"


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
async def test_upload_media(client: WhatsAppClient, image_path: str):
    with open(image_path, "rb") as f:
        media_resp = await client.upload(f.read(), mimetypes.guess_type(image_path)[0])

    media_id = media_resp.media.pop().id
    assert media_id is not None
    return media_id


@pytest.mark.asyncio
async def test_send_image_local(client: WhatsAppClient, to: str, image_path: str):
    media_id = await test_upload_media(client, image_path)
    await client.send_image(to, media_id=media_id)


@pytest.mark.asyncio
async def test_send_image_url(client: WhatsAppClient, to: str, image_url: str):
    resp = await client.send_image(to, media_link=image_url)


@pytest.mark.asyncio
async def test_send_document_local(client: WhatsAppClient, to: str, document_path: str):
    media_id = await test_upload_media(client, document_path)
    await client.send_document(
        to, media_id=media_id, filename="test.pdf", caption="Test"
    )


@pytest.mark.asyncio
async def test_send_document_url(client: WhatsAppClient, to: str, document_url: str):
    resp = await client.send_document(
        to, media_link=document_url, filename="test.pdf", caption="Test"
    )


@pytest.mark.asyncio
async def test_send_audio_local(client: WhatsAppClient, to: str, audio_path: str):
    media_id = await test_upload_media(client, audio_path)
    await client.send_audio(to, media_id=media_id)


@pytest.mark.asyncio
async def test_send_audio_url(client: WhatsAppClient, to: str, audio_url: str):
    resp = await client.send_audio(to, media_link=audio_url)


@pytest.mark.asyncio
async def test_send_video_local(client: WhatsAppClient, to: str, video_path: str):
    media_id = await test_upload_media(client, video_path)
    await client.send_video(to, media_id=media_id)


@pytest.mark.asyncio
async def test_send_video_url(client: WhatsAppClient, to: str, video_url: str):
    resp = await client.send_video(to, media_link=video_url)
