from enum import Enum
from typing import Optional, Union

from pydantic import RootModel, model_validator, BaseModel, Field


class MediaTypes(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    STICKER = "sticker"


class Thumbnail(BaseModel):
    link: Optional[str] = None
    data: Optional[str] = Field(None, description="base64 encoded image data")

    @model_validator(mode="before")
    @classmethod
    def validate_link_or_data(cls, values):
        if not values.get("data") and not values.get("link"):
            raise ValueError("Either link or data must be provided")

        return values


class BaseMedia(BaseModel):
    id: Optional[str] = None
    link: Optional[str] = None
    caption: Optional[str] = None
    filename: Optional[str] = None
    provider: Optional[str] = None
    thumbnail: Optional[Thumbnail] = None

    @model_validator(mode="before")
    def validate_one_of_sources(cls, values: dict):
        if not any([values.get("id"), values.get("link")]):
            raise ValueError(
                "Invalid media source. one of id or link must be specified"
            )
        return values


# media by id


class ImageById(BaseMedia):
    id: str


class AudioById(BaseMedia):
    id: str


class VideoById(BaseMedia):
    id: str


class DocumentById(BaseMedia):
    id: str
    filename: str


# media by provider


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


# final models for media objects


class RootModelMixin:
    @property
    def __root__(self):
        return self.root


class Image(RootModelMixin, RootModel[Union[ImageById, ImageByProvider]]):
    root: Union[ImageById, ImageByProvider] = Field(
        ..., description="The media object containing an image", title="Image"
    )


class Audio(RootModelMixin, RootModel[Union[AudioById, AudioByProvider]]):
    root: Union[AudioById, AudioByProvider] = Field(
        ..., description="The media object containing audio", title="Audio"
    )


class Video(RootModelMixin, RootModel[Union[VideoById, VideoByProvider]]):
    root: Union[VideoById, VideoByProvider] = Field(
        ..., description="The media object containing a video", title="Video"
    )


class Document(RootModelMixin, RootModel[Union[DocumentById, DocumentByProvider]]):
    root: Union[DocumentById, DocumentByProvider] = Field(
        ..., description="The media object containing a document", title="Document"
    )


class Media(RootModelMixin, RootModel[Union[Image, Audio, Video, Document]]):
    root: Union[Image, Audio, Video, Document] = Field(
        ..., description="The media object containing a media", title="Media"
    )
