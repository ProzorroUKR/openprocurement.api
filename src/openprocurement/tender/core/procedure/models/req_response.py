from logging import getLogger
from typing import Any
from uuid import uuid4

from pydantic import Field, field_serializer, field_validator

from openprocurement.api.procedure.models.base import (
    Model,
    model_field_validator,
    validate_list_uniq_factory,
    validate_object_id_uniq,
)
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.models.reference import (
    Reference,
    RequirementReference,
)
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
)
from openprocurement.api.procedure.value_types import TYPEMAP
from openprocurement.tender.core.procedure.models.criterion import validate_value_type
from openprocurement.tender.core.procedure.models.evidence import Evidence
from openprocurement.tender.core.procedure.utils import (
    get_requirement_obj,
)

LOGGER = getLogger(__name__)


class ExtendPeriod(Period):
    maxExtendDate: IsoDateTime | None = None
    durationInDays: int | None = None
    duration: str | None = None


class BaseRequirementResponse(Model):
    period: ExtendPeriod | None = None
    requirement: RequirementReference
    relatedTenderer: Reference | None = None
    relatedItem: MD5 | None = None
    evidences: list[Evidence] = []
    value: Any = None
    values: list[Any] | None = None

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

    @field_serializer("value")
    def serialize_value(self, value: Any) -> Any:
        converted = self.convert_value()
        return value if converted is None else converted

    @field_serializer("values")
    def serialize_values(self, value: Any) -> Any:
        converted = self.convert_values()
        return value if converted is None else converted

    @model_field_validator("value")
    def validate_value(self, value):
        if value and self.requirement:
            requirement, *_ = get_requirement_obj(self.requirement.id)
            if requirement:
                validate_value_type(value, requirement["dataType"])

    @model_field_validator("values")
    def validate_values(self, values):
        if values and self.requirement:
            requirement, *_ = get_requirement_obj(self.requirement.id)
            if requirement:
                for value in values:
                    validate_value_type(value, requirement["dataType"])

    @field_validator("evidences")
    @classmethod
    def validate_evidences_items(cls, value):
        validate_object_id_uniq(value)
        return value


class PatchRequirementResponse(BaseRequirementResponse):
    requirement: RequirementReference | None = None


class RequirementResponse(BaseRequirementResponse):
    id: MD5 = Field(default_factory=lambda: uuid4().hex)


validate_response_requirement_uniq = validate_list_uniq_factory("requirement.id", err_field="requirement")


class ObjResponseMixin(Model):
    """the responses are validated by the state of the bid / award / qualification (RequirementResponsesRulesMixin)"""

    requirementResponses: list[RequirementResponse] | None = None

    @field_validator("requirementResponses")
    @classmethod
    def validate_requirement_responses_items(cls, value):
        validate_object_id_uniq(value)
        validate_response_requirement_uniq(value)
        return value
