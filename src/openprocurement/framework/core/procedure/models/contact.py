from schematics.types import EmailType, StringType

from openprocurement.api.procedure.models.contact import (
    ContactPoint as BaseContactPoint,
)
from openprocurement.api.procedure.models.contact import (
    validate_email,
    validate_telephone,
)


class CommonContactPoint(BaseContactPoint):
    def validate_email(self, contact_point, email):
        validate_email(contact_point, email)

    def validate_telephone(self, _, telephone):
        validate_telephone(telephone)


class ContactPoint(CommonContactPoint):
    email = EmailType(required=True)


class PatchContactPoint(ContactPoint):
    name = StringType()
    email = EmailType()


class SubmissionContactPoint(BaseContactPoint):
    email = EmailType(required=True)

    def validate_email(self, data, value):
        validate_email(data, value)
