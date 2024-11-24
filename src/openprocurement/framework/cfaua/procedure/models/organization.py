from schematics.types import StringType

from openprocurement.api.procedure.models.address import Address
from openprocurement.api.procedure.models.organization import (
    PROCURING_ENTITY_KINDS,
    Organization,
)
from openprocurement.api.procedure.types import ListType, ModelType
from openprocurement.framework.core.procedure.models.contact import (
    CommonContactPoint as BaseContactPoint,
)


class ContactPoint(BaseContactPoint):
    availableLanguage = StringType(required=True, choices=["uk", "en", "ru"], default="uk")

    def validate_telephone(self, data, value):
        pass


class ProcuringEntity(Organization):
    """An organization."""

    kind = StringType(choices=PROCURING_ENTITY_KINDS)
    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True), required=False)
    address = ModelType(Address, required=True)
