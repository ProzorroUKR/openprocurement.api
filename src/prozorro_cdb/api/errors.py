from aiohttp import web

from openprocurement.api.utils import json_dumps


class BaseJsonHTTPError(web.HTTPClientError):  # RFC 9457
    type: str
    title: str
    status_code: int

    def __init__(
        self,
        *,
        details: str,
        **extra,
    ) -> None:
        payload = {
            "type": self.type,
            "title": self.title,
            "details": details,
            "status": self.status_code,
            **extra,
        }
        super().__init__(text=json_dumps(payload, ensure_ascii=False), content_type="application/json")


# base http errors


class JsonHTTPBadRequest(BaseJsonHTTPError):
    status_code = 400
    type = "http-bad-request"
    title = "Bad Request"


class JsonHTTPNotFound(BaseJsonHTTPError):
    status_code = 404
    type = "http-not-found"
    title = "Not Found"


# custom http errors


class ModelValidationHttpError(JsonHTTPBadRequest):
    status_code = 400
    type = "data-validation"
    title = "Data Validation Error"
