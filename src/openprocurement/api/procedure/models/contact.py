import re

from schematics.types import EmailType, StringType
from schematics.validate import ValidationError

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import URLType


class ContactPoint(Model):
    name = StringType(required=True)
    name_en = StringType()
    name_ru = StringType()
    email = EmailType()
    telephone = StringType()
    faxNumber = StringType()
    url = URLType()


def validate_telephone(telephone):
    if telephone and re.match(r"^(\+)?[0-9]{2,}(,( )?(\+)?[0-9]{2,})*$", telephone) is None:
        raise ValidationError("wrong telephone format (could be missed +)")


def validate_email(contact_point, email):
    if not email and not contact_point.get("telephone"):
        raise ValidationError("telephone or email should be present")
