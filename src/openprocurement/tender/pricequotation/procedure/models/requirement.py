from schematics.types import StringType, MD5Type
from schematics.types.compound import ModelType
from schematics.validate import ValidationError
from uuid import uuid4
from openprocurement.api.models import Model
from openprocurement.api.utils import get_first_revision_date
from openprocurement.api.constants import PQ_CRITERIA_ID_FROM
from openprocurement.tender.core.validation import validate_value_type
from openprocurement.tender.core.procedure.context import get_tender, get_now
from openprocurement.tender.core.procedure.models.unit import Unit as BaseUnit


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
    if objs:
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
    minValue = StringType()
    maxValue = StringType()
    expectedValue = StringType()

    def validate_minValue(self, data, value):
        validate_value_type(value, data['dataType'])

    def validate_maxValue(self, data, value):
        validate_value_type(value, data['dataType'])

    def validate_expectedValue(self, data, value):
        validate_value_type(value, data['dataType'])