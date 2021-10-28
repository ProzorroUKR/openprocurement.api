from schematics.types import StringType, MD5Type
from schematics.types.compound import ModelType
from schematics.exceptions import ValidationError

from openprocurement.api.models import ListType, Model
from openprocurement.tender.pricequotation.models.requirement import Requirement
from openprocurement.tender.core.validation import validate_requirement_groups
from openprocurement.tender.core.models import get_tender


class RequirementGroup(Model):
    id = StringType(required=True)
    description = StringType(required=True)
    requirements = ListType(ModelType(Requirement, required=True), default=list())


class Criterion(Model):
    id = StringType(required=True)
    title = StringType(required=True)
    description = StringType(required=True)
    relatesTo = StringType(choices=["item"])
    relatedItem = MD5Type()
    requirementGroups = ListType(ModelType(RequirementGroup),
                                 required=True,
                                 validators=[validate_requirement_groups])

    def validate_relatedItem(self, data, relatedItem):
        if not relatedItem and data.get("relatesTo"):
            raise ValidationError("This field is required.")
        parent = data["__parent__"]
        if relatedItem and isinstance(parent, Model):
            tender = get_tender(parent)
            if relatedItem not in [i.id for i in tender.items if i]:
                raise ValidationError("relatedItem should be one of items")
