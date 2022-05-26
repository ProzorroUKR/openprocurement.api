from schematics.types import BaseType, StringType, IntType, MD5Type
from schematics.types.compound import ModelType
from schematics.transforms import blacklist
from schematics.validate import ValidationError
from uuid import uuid4
from openprocurement.api.models import schematics_default_role, schematics_embedded_role
from openprocurement.api.models import Model, ListType
from openprocurement.api.models import Unit as BaseUnit
from openprocurement.api.utils import get_now, get_first_revision_date
from openprocurement.api.constants import PQ_CRITERIA_ID_FROM
from openprocurement.tender.pricequotation.validation import validate_value_type, validate_list_of_values_type
from openprocurement.tender.core.models import get_tender


class Unit(BaseUnit):
    name = StringType(required=True)


class ValidateIdMixing(Model):
    id = StringType(required=True, default=lambda: uuid4().hex)

    def validate_id(self, data, value):
        tender = get_tender(data["__parent__"])
        if get_first_revision_date(tender, default=get_now()) > PQ_CRITERIA_ID_FROM:
            field = MD5Type()
            value = field.to_native(value)
            field.validate(value)


def validate_criteria_id_uniq(objs, *args):
    if objs:
        tender = get_tender(objs[0])
        if get_first_revision_date(tender, default=get_now()) > PQ_CRITERIA_ID_FROM:
            ids = [i.id for i in objs]
            if len(set(ids)) != len(ids):
                raise ValidationError("Criteria id should be uniq")

            rg_ids = [rg.id for c in objs for rg in c.requirementGroups]
            if len(rg_ids) != len(set(rg_ids)):
                raise ValidationError("Requirement group id should be uniq in tender")

            req_ids = [req.id for c in objs for rg in c.requirementGroups for req in rg.requirements]
            if len(req_ids) != len(set(req_ids)):
                raise ValidationError("Requirement id should be uniq for all requirements in tender")


class Requirement(ValidateIdMixing, Model):
    class Options:
        namespace = "Requirement"
        roles = {
            "create": blacklist(),
            "edit_draft": blacklist(),
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
        }

    title = StringType(required=True)
    description = StringType()
    dataType = StringType(required=True,
                          choices=["string", "number", "integer", "boolean"])
    unit = ModelType(Unit)
    # should be updated cause cancellation isn't
    # refactored and on cancellation validating uses this model with old tender
    minValue = BaseType()
    maxValue = BaseType()
    expectedValue = BaseType()

    expectedValues = ListType(BaseType(required=True), default=list)
    expectedMinItems = IntType(min_value=1)
    expectedMaxItems = IntType(min_value=1)

    def validate_minValue(self, data, value):
        validate_value_type(value, data['dataType'])

    def validate_maxValue(self, data, value):
        validate_value_type(value, data['dataType'])

    def validate_expectedValue(self, data, value):
        validate_value_type(value, data['dataType'])

    def validate_expectedValues(self, data, value):
        validate_list_of_values_type(value, data['dataType'])
