from dataclasses import field, dataclass
from json import JSONDecodeError
from typing import Dict, List, Tuple, Union

from aiohttp import ClientSession
from loguru import logger
from pydantic import BaseModel

from whatsapp import errors, messages, responses

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
                "X-Wa-Id": self.config.wa_id,
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
        if data := kwargs.pop("data", {}):
            # TODO: use custom json encoder
            if isinstance(data, BaseModel):
                kwargs["json"] = data.dict()

        # TODO: some logging
        async with self.session.request(method, url, **kwargs) as resp:
            model_resp: BaseModel = None

            try:
                json_data = await resp.json()
                text_data = None
            except JSONDecodeError:
                # TODO: some logging
                json_data = {}
                text_data = await resp.text()

            resp.raise_for_status()
            if response_model:
                with logger.catch(
                    level="WARNING",
                    message=f"Failed to parse response as {response_model.__name__}",
                ):
                    model_resp = response_model(**json_data)

            if isinstance(model_resp, responses.Response) and not model_resp.success:
                raise errors.RequestError(model_resp.message, model_resp.data)

            return model_resp or json_data or text_data

    async def login(self):
        if self.config.is_logged_in:
            raise errors.LoginError("Already logged in")
        else:
            resp: responses.LoginResponse = await self._do_request(
                "POST",
                f"{self.config.endpoint}/accounts",
                data=messages.AccountInfo(id=self.config.wa_id, webhook_url=None),
                response_model=responses.LoginResponse,
            )
            self.config.token = resp.data.token
            # update headers
            self.__post_init__()
            return resp

    @needs_login
    async def send(self, *args, **kwargs) -> responses.Response:
        return await self._do_request(
            "POST",
            f"{self.config.endpoint}/messages",
            *args,
            data=kwargs.pop("data", {}),
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
