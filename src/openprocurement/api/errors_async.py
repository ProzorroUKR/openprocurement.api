from aiohttp import web

from openprocurement.api.utils import json_dumps


class BaseJsonHTTPError(web.HTTPClientError):
    def __init__(
        self,
        *,
        message: str = "Bad Request",
        **extra,
    ) -> None:
        payload = {"errors": [message], **extra}
        super().__init__(text=json_dumps(payload, ensure_ascii=False), content_type="application/json")


class JsonHTTPBadRequest(BaseJsonHTTPError):
    status_code = 400


class JsonHTTPNotFound(BaseJsonHTTPError):
    status_code = 404
