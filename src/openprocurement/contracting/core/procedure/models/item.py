from typing import Any, ClassVar

from pydantic import field_serializer

from openprocurement.api.procedure.models.address import Address
from openprocurement.api.procedure.models.base import Model, model_field_validator
from openprocurement.api.procedure.models.item import (
    AdditionalClassification as BaseAdditionalClassification,
)
from openprocurement.api.procedure.models.item import (
    CPVClassification as BaseCPVClassification,
)
from openprocurement.api.procedure.models.item import Item as BaseItem
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.models.unit import Unit
from openprocurement.api.procedure.types import (
    MD5,
)
from openprocurement.api.procedure.utils import to_decimal


class CPVClassification(BaseCPVClassification):
    dk021_scheme_required: ClassVar[bool] = False


class AdditionalClassification(BaseAdditionalClassification):
    @model_field_validator("id")
    def validate_id(self, value):
        pass  # the ids of the dictionaries aren't checked


class Attribute(Model):
    name: str
    unit: Unit | None = None
    values: list[Any] | None = None
    value: Any = None
    dataSchema: str | None = None

    @field_serializer("value")
    def serialize_value(self, value: Any) -> Any:
        if value and isinstance(value, float):
            return to_decimal(value)
        return value

    @field_serializer("values")
    def serialize_values(self, values: list | None) -> Any:
        if values:
            return [to_decimal(value) if isinstance(value, float) else value for value in values]
        return values


class Item(BaseItem):
    classification: CPVClassification
    additionalClassifications: list[AdditionalClassification] = []
    unit: Unit | None = None
    deliveryAddress: Address | None = None
    deliveryDate: Period | None = None
    relatedLot: MD5 | None = None
    relatedBuyer: MD5 | None = None
    attributes: list[Attribute] | None = None
    product: str | None = None
    category: str | None = None
