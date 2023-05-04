from schematics.types import BaseType, StringType, IntType, MD5Type
from schematics.types.compound import ModelType
from schematics.validate import ValidationError
from uuid import uuid4
from openprocurement.api.context import get_now
from openprocurement.api.models import Model, ListType
from openprocurement.api.utils import get_first_revision_date
from openprocurement.api.constants import PQ_CRITERIA_ID_FROM
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.models.unit import Unit as BaseUnit
from openprocurement.tender.pricequotation.validation import validate_value_type, validate_list_of_values_type


class Unit(BaseUnit):
    name = StringType(required=True)


class ValidateIdMixing(Model):
    id = StringType(required=True, default=lambda: uuid4().hex)

    def validate_id(self, data, value):
        tender = get_tender()
        if get_first_revision_date(tender, default=get_now()) > PQ_CRITERIA_ID_FROM:
            field = MD5Type()
            value = field.to_native(value)
            field.validate(value)


def validate_criteria_id_uniq(objs, *args):
    if not objs:
        return
    tender = get_tender()
    if get_first_revision_date(tender, default=get_now()) > PQ_CRITERIA_ID_FROM:
        ids = [i.id for i in objs]
        if len(set(ids)) != len(ids):
            raise ValidationError("Criteria id should be uniq")

        rg_ids = [rg.id
                  for c in objs
                  for rg in c.requirementGroups or ""]
        if len(rg_ids) != len(set(rg_ids)):
            raise ValidationError("Requirement group id should be uniq in tender")

        req_ids = [req.id
                   for c in objs
                   for rg in c.requirementGroups or ""
                   for req in rg.requirements or ""]
        if len(req_ids) != len(set(req_ids)):
            raise ValidationError("Requirement id should be uniq for all requirements in tender")


class Requirement(ValidateIdMixing, Model):

    title = StringType(required=True)
    description = StringType()
    dataType = StringType(required=True,
                          choices=["string", "number", "integer", "boolean"])
    unit = ModelType(Unit)
    minValue = BaseType()
    maxValue = BaseType()
    expectedValue = BaseType()

    expectedValues = ListType(BaseType(required=True), min_size=1)
    expectedMinItems = IntType(min_value=0)
    expectedMaxItems = IntType(min_value=0)

    def validate_minValue(self, data, value):
        return validate_value_type(value, data['dataType'])

    def validate_maxValue(self, data, value):
        return validate_value_type(value, data['dataType'])

    def validate_expectedValue(self, data, value):
        return validate_value_type(value, data['dataType'])

    def validate_expectedValues(self, data, value):
        return validate_list_of_values_type(value, data['dataType'])

