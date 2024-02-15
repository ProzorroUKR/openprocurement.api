from openprocurement.api.procedure.models.contact import (
    ContactPoint as BaseContactPoint,
)
from openprocurement.api.procedure.models.contact import (
    validate_email,
    validate_telephone,
)


class ContactPoint(BaseContactPoint):
    def validate_email(self, contact_point, email):
        validate_email(contact_point, email)

    def validate_telephone(self, _, telephone):
        validate_telephone(telephone)
