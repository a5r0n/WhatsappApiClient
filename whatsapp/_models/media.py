import base64
from enum import Enum
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field, root_validator


class MediaTypes(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    STICKER = "sticker"


class Thumbnail(BaseModel):
    link: Optional[str]
    data: Optional[str] = Field(None, description="base64 encoded image data")

    @root_validator(pre=True)
    def validate_link_or_data(cls, values):
        if not values.get("data") and not values.get("link"):
            raise ValueError("Either link or data must be provided")

        return values


class BaseMedia(BaseModel):
    id: Optional[str]
    link: Optional[str]
    caption: Optional[str]
    filename: Optional[str]
    provider: Optional[str]
    thumbnail: Optional[Thumbnail]

    @root_validator
    def validate_one_of_sources(cls, values: dict):
        if not any([values.get("id"), values.get("link")]):
            raise ValueError(
                "Invalid media source. one of id or link must be specified"
            )
        return values


## media by id


class ImageById(BaseMedia):
    id: str


class AudioById(BaseMedia):
    id: str


class VideoById(BaseMedia):
    id: str


class DocumentById(BaseMedia):
    id: str
    filename: str


## media by provider


class Provider(BaseModel):
    name: str


class ImageByProvider(BaseMedia):
    link: str


class AudioByProvider(BaseMedia):
    link: str


class VideoByProvider(BaseMedia):
    link: str


class DocumentByProvider(BaseMedia):
    link: str
    filename: str


## final models for media objects


class Image(BaseModel):
    __root__: Union[ImageById, ImageByProvider] = Field(
        ..., description="The media object containing an image", title="Image"
    )


class Audio(BaseModel):
    __root__: Union[AudioById, AudioByProvider] = Field(
        ..., description="The media object containing audio", title="Audio"
    )


class Video(BaseModel):
    __root__: Union[VideoById, VideoByProvider] = Field(
        ..., description="The media object containing a video", title="Video"
    )


class Document(BaseModel):
    __root__: Union[DocumentById, DocumentByProvider] = Field(
        ..., description="The media object containing a document", title="Document"
    )


class Media(BaseModel):
    __root__: Union[Image, Audio, Video, Document] = Field(
        ..., description="The media object containing a media", title="Media"
    )
