from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.api.context import get_now
from openprocurement.api.models import Model
from openprocurement.api.constants import VALIDATE_TELEPHONE_FROM
from openprocurement.api.utils import get_first_revision_date
from schematics.types import StringType, EmailType, URLType
from schematics.validate import ValidationError
import re


class PatchContactPoint(Model):
    name = StringType()
    name_en = StringType()
    name_ru = StringType()
    email = EmailType()
    telephone = StringType()
    faxNumber = StringType()
    url = URLType()

    def validate_telephone(self, _, value):
        tender = get_tender()
        if (
            get_first_revision_date(tender, default=get_now()) >= VALIDATE_TELEPHONE_FROM
            and value
            and re.match(r"^(\+)?[0-9]{2,}(,( )?(\+)?[0-9]{2,})*$", value) is None
        ):
            raise ValidationError(u"wrong telephone format (could be missed +)")


class PostContactPoint(PatchContactPoint):
    name = StringType(required=True)

    def validate_email(self, data, value):
        if not value and not data.get("telephone"):
            raise ValidationError("telephone or email should be present")


class ContactPoint(PostContactPoint):
    pass

