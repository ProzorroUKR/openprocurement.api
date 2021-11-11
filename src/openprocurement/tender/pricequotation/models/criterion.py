from schematics.types import StringType, MD5Type
from schematics.types.compound import ModelType
from schematics.exceptions import ValidationError

from openprocurement.api.models import ListType, Model
from openprocurement.api.utils import get_now, get_first_revision_date
from openprocurement.tender.pricequotation.models.requirement import Requirement
from openprocurement.tender.core.validation import validate_requirement_groups
from openprocurement.tender.core.models import get_tender

from openprocurement.api.constants import PQ_MULTI_PROFILE_FROM


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
        multi_profile_released = get_first_revision_date(data, default=get_now()) > PQ_MULTI_PROFILE_FROM

        if not multi_profile_released and relatedItem:
            raise ValidationError("Rogue field.")

        if not relatedItem and data.get("relatesTo"):
            raise ValidationError("This field is required.")
        parent = data["__parent__"]
        if relatedItem and isinstance(parent, Model):
            tender = get_tender(parent)
            if relatedItem not in [i.id for i in tender.items if i]:
                raise ValidationError("relatedItem should be one of items")

    def validate_relatesTo(self, data, relatesTo):
        multi_profile_released = get_first_revision_date(data, default=get_now()) > PQ_MULTI_PROFILE_FROM

        if not multi_profile_released and relatesTo:
            raise ValidationError("Rogue field.")
