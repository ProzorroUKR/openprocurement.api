from schematics.types import StringType

from openprocurement.api.procedure.models.contact import ContactPoint as BaseContactPoint, validate_email


class ContactPoint(BaseContactPoint):
    availableLanguage = StringType()

    def validate_email(self, contact_point, email):
        validate_email(contact_point, email)
