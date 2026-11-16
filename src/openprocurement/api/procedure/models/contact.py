import re

from openprocurement.api.constants_env import VALIDATE_TELEPHONE_FROM
from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import Email, Url


class ContactPoint(Model):
    name: str
    name_en: str | None = None
    name_ru: str | None = None
    email: Email | None = None
    telephone: str | None = None
    faxNumber: str | None = None
    url: Url | None = None


def validate_telephone(telephone: str | None) -> None:
    if VALIDATE_TELEPHONE_FROM <= get_request_now():
        if telephone and re.match(r"^(\+)?[0-9]{2,}(,( )?(\+)?[0-9]{2,})*$", telephone) is None:
            raise ValueError("wrong telephone format (could be missed +)")


def validate_email(email: str | None, telephone: str | None) -> None:
    if not email and not telephone:
        raise ValueError("telephone or email should be present")
