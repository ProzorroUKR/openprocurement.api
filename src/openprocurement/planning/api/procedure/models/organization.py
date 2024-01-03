from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import StringType, BaseType, MD5Type

from openprocurement.api.constants import PLAN_ADDRESS_KIND_REQUIRED_FROM
from openprocurement.api.models import Model, PROCURING_ENTITY_KINDS
from openprocurement.api.procedure.utils import is_obj_const_active
from openprocurement.api.procedure.models.base import ModelType
from openprocurement.api.procedure.models.identifier import Identifier
from openprocurement.planning.api.procedure.context import get_plan
from openprocurement.planning.api.procedure.models.address import Address
from openprocurement.tender.core.procedure.models.identifier import Identifier


class BaseOrganization(Model):
    id = MD5Type(default=lambda: uuid4().hex)
    name = StringType(required=True)
    name_en = StringType()
    name_ru = StringType()
    identifier = ModelType(Identifier, required=True)
    address = ModelType(Address)
    kind = StringType(choices=PROCURING_ENTITY_KINDS)


class PlanOrganization(BaseOrganization):
    def validate_address(self, organization, address):
        validate_address_kind_required(address)

    def validate_kind(self, organization, kind):
        validate_address_kind_required(kind)


def validate_address_kind_required(value):
    if not value and is_obj_const_active(get_plan(), PLAN_ADDRESS_KIND_REQUIRED_FROM):
        raise ValidationError(BaseType.MESSAGES["required"])
