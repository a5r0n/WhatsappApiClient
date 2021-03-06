from dataclasses import field, dataclass
from json import JSONDecodeError
from typing import Dict, List, Tuple, Union

from aiohttp import ClientSession
from aiohttp.client_exceptions import ContentTypeError
from loguru import logger
from pydantic import BaseModel, ValidationError

from whatsapp import errors, messages, responses
from whatsapp._models.media import Media, MediaTypes

from .config import WhatsAppConfig
from .utils import needs_login


@dataclass
class Client:
    config: WhatsAppConfig = field(default_factory=WhatsAppConfig)
    session: ClientSession = field(default_factory=ClientSession)

    def __post_init__(self):
        self.session.headers.update(
            {
                "User-Agent": self.config.user_agent,
                "X-Wa-Id": self.config.wa_id or "",
                "Authorization": (
                    f"Bearer {self.config.token}" if self.config.token else ""
                ),
            }
        )

    async def __aenter__(self):
        await self.session.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.__aexit__(exc_type, exc_val, exc_tb)

    async def _do_request(
        self, method, url, response_model: BaseModel = None, **kwargs
    ) -> Union[BaseModel, Dict, str, None]:
        if data := kwargs.pop("data", None):
            # TODO: use custom json encoder
            if isinstance(data, BaseModel):
                kwargs["json"] = data.dict(exclude_none=True)
                data = None

        logger.debug(f"{method} {url} {kwargs}")

        async with self.session.request(method, url, **kwargs, data=data) as resp:
            model_resp: BaseModel = None

            try:
                json_data = await resp.json()
                text_data = None
            except ContentTypeError:
                json_data = None
                text_data = await resp.text()
                try:
                    model_resp = response_model.parse_raw(text_data)
                except Exception as e:
                    logger.warning(f"Failed to parse response: {text_data} {e}")
            except JSONDecodeError:
                # TODO: some logging
                json_data = {}
                text_data = await resp.text()

            if response_model:
                try:
                    model_resp = response_model.parse_obj(json_data)
                except ValidationError as e:
                    model_resp = None
                    logger.bind(response=resp, data=json_data, error=e).warning(
                        f"Failed to parse response as {response_model.__name__} {e}"
                    )

            if isinstance(model_resp, responses.Response) and not model_resp.success:
                raise errors.RequestError(model_resp.message, model_resp.data)

            resp.raise_for_status()
            return model_resp or json_data or text_data

    async def login(self, webhook_url: str = None, only_status_updates: bool = False):
        if self.config.is_logged_in:
            raise errors.LoginError("Already logged in")
        else:
            resp: responses.LoginResponse = await self._do_request(
                "POST",
                f"{self.config.endpoint}/accounts",
                data=messages.AccountInfo(
                    webhook_url=webhook_url, only_status_updates=only_status_updates
                ),
                response_model=responses.LoginResponse,
            )
            self.config.token = resp.data.token
            # update headers
            self.__post_init__()
            return resp

    @needs_login
    async def logout(self):
        resp: responses.LogoutResponse = await self._do_request(
            "DELETE",
            f"{self.config.endpoint}/accounts",
            response_model=responses.LogoutResponse,
        )
        self.config.token = None
        return resp

    async def status(self):
        resp: responses.StatusResponse = await self._do_request(
            "GET",
            f"{self.config.endpoint}/status",
            response_model=responses.StatusResponse,
        )
        return resp

    @needs_login
    async def groups(self):
        resp: responses.GroupsResponse = await self._do_request(
            "GET",
            f"{self.config.endpoint}/groups",
            response_model=responses.GroupsResponse,
        )
        return resp

    @needs_login
    async def upload(self, data: bytes, mime_type: str) -> responses.UploadResponse:
        resp: responses.UploadResponse = await self._do_request(
            "POST",
            f"{self.config.endpoint}/media",
            data=data,
            response_model=responses.UploadResponse,
            headers={"Content-Type": mime_type},
        )
        return resp

    @needs_login
    async def send(self, *args, **kwargs) -> responses.Response:
        data = kwargs.pop("data", None)
        if isinstance(data, messages.Message) and data.preview_url is None:
            data.preview_url = self.config.defaults.preview_url

        return await self._do_request(
            "POST",
            f"{self.config.endpoint}/messages",
            *args,
            data=data,
            response_model=responses.Response,
            **kwargs,
        )

    async def send_text(self, to: str, text: str, *args, **kwargs):
        message = messages.Message(
            to=to,
            type=messages.MessageType.TEXT,
            text=messages.Text(body=text),
            # TODO: include kwargs
            **{},
        )
        return await self.send(data=message, *args, **kwargs)

    async def send_buttons(self, to: str, text: str, buttons: List[Tuple[str, str]]):
        message = messages.Message(
            to=to,
            type=messages.MessageType.INTERACTIVE,
            interactive=messages.interactive.InteractiveButtons(
                body=messages.interactive.Text(text=text),
                action=messages.interactive.ButtonsAction(
                    buttons=[
                        messages.interactive.Button(
                            reply=messages.interactive.ButtonRow(
                                id=id,
                                title=title,
                                description=args[0] if args else None,
                            )
                        )
                        for id, title, *args in buttons
                    ]
                ),
            ),
        )
        return await self.send(data=message)

    async def send_list(
        self,
        to: str,
        text: str,
        title: str,
        buttons: List[Tuple[str, str]],
        button: str = None,
    ):
        button = button or title

        message = messages.Message(
            to=to,
            type=messages.MessageType.INTERACTIVE,
            interactive=messages.interactive.InteractiveList(
                body=messages.interactive.Text(text=text),
                action=messages.interactive.ListAction(
                    button=button,
                    sections=[
                        messages.interactive.Section(
                            title=title,
                            rows=[
                                messages.interactive.SectionRow(
                                    id=id,
                                    title=title,
                                    description=args[0] if args else None,
                                )
                                for id, title, *args in buttons
                            ],
                        )
                    ],
                ),
            ),
        )
        return await self.send(data=message)

    async def send_media(
        self, to, type: str, media_id=None, media_link=None, *args, **kwargs
    ):
        try:
            media = Media.parse_obj(
                {
                    "type": type,
                    "id": media_id,
                    "link": media_link,
                    "caption": kwargs.pop("caption", None),
                    "filename": kwargs.pop("filename", None),
                }
            )
            logger.debug(f"{media}")
        except ValidationError:
            raise ValueError("Either media_id or media_link must be specified")

        message = messages.Message.parse_obj(
            {
                "to": to,
                "type": type,
                type: media,
            }
        )
        return await self.send(data=message, *args, **kwargs)

    async def send_image(self, *args, caption: str = None, **kwargs):
        return await self.send_media(*args, type="image", caption=caption, **kwargs)

    async def send_video(self, *args, caption: str = None, **kwargs):
        return await self.send_media(*args, type="video", caption=caption, **kwargs)

    async def send_audio(self, *args, **kwargs):
        return await self.send_media(*args, type="audio", **kwargs)

    async def send_document(self, *args, filename: str = None, **kwargs):
        return await self.send_media(
            *args, type="document", filename=filename, **kwargs
        )
