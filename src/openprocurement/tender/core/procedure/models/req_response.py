from logging import getLogger
from uuid import uuid4

from schematics.types import BaseType, IntType, MD5Type, StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.models.reference import (
    Reference,
    RequirementReference,
)
from openprocurement.api.procedure.types import IsoDateTimeType, ListType
from openprocurement.api.validation import validate_list_uniq_factory
from openprocurement.tender.core.procedure.models.evidence import Evidence
from openprocurement.tender.core.procedure.utils import (
    get_requirement_obj,
)
from openprocurement.tender.core.procedure.validation import (
    TYPEMAP,
    validate_object_id_uniq,
    validate_value_type,
)

LOGGER = getLogger(__name__)


class ExtendPeriod(Period):
    maxExtendDate = IsoDateTimeType()
    durationInDays = IntType()
    duration = StringType()


# ECriteria


class BaseRequirementResponse(Model):
    period = ModelType(ExtendPeriod)
    requirement = ModelType(RequirementReference, required=True)
    relatedTenderer = ModelType(Reference)
    relatedItem = MD5Type()
    evidences = ListType(
        ModelType(Evidence, required=True),
        default=[],
        validators=[validate_object_id_uniq],
    )

    value = BaseType()
    values = ListType(BaseType(required=True))

    def convert_value(self):
        if self.requirement:
            requirement, *_ = get_requirement_obj(self.requirement.id)
            if requirement:
                return TYPEMAP[requirement["dataType"]](self.value) if self.value else None
        return self.value

    def convert_values(self):
        if self.requirement:
            requirement, *_ = get_requirement_obj(self.requirement.id)
            if requirement:
                return [TYPEMAP[requirement["dataType"]](value) for value in self.values] if self.values else None
        return self.values

    @serializable(serialized_name="value", serialize_when_none=False)
    def serialize_value(self):
        return self.convert_value()

    @serializable(serialized_name="values", serialize_when_none=False)
    def serialize_values(self):
        return self.convert_values()

    def validate_value(self, data, value):
        if value and data.get("requirement"):
            requirement, *_ = get_requirement_obj(data["requirement"]["id"])
            if requirement:
                validate_value_type(value, requirement["dataType"])

    def validate_values(self, data, values):
        if values and data.get("requirement"):
            requirement, *_ = get_requirement_obj(data["requirement"]["id"])
            if requirement:
                for value in values:
                    validate_value_type(value, requirement["dataType"])


class PatchRequirementResponse(BaseRequirementResponse):
    requirement = ModelType(RequirementReference)


class RequirementResponse(BaseRequirementResponse):
    id = MD5Type(required=True, default=lambda: uuid4().hex)


# Validations ---


validate_response_requirement_uniq = validate_list_uniq_factory("requirement.id", err_field="requirement")


# --- Validations


# Bid requirementResponses mixin ---


class ObjResponseMixin(Model):
    """the responses are validated by the state of the bid / award / qualification (RequirementResponsesRulesMixin)"""

    requirementResponses = ListType(
        ModelType(RequirementResponse, required=True),
        validators=[validate_object_id_uniq, validate_response_requirement_uniq],
    )

    # --- requirementResponses mixin
