from schematics.exceptions import ValidationError
from schematics.types import MD5Type, StringType
from schematics.types.compound import ModelType

from openprocurement.api.constants import PQ_MULTI_PROFILE_FROM
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import ListType
from openprocurement.api.utils import get_first_revision_date, get_now
from openprocurement.tender.pricequotation.procedure.models.requirement import (
    Requirement,
    ValidateIdMixing,
)
from openprocurement.tender.pricequotation.procedure.validation import (
    validate_requirement_groups,
)


class RequirementGroup(ValidateIdMixing, Model):
    description = StringType(required=True)
    requirements = ListType(ModelType(Requirement, required=True), required=True, min_size=1)


class Criterion(ValidateIdMixing, Model):
    title = StringType(required=True)
    description = StringType(required=True)
    relatesTo = StringType(choices=["item"])
    relatedItem = MD5Type()
    requirementGroups = ListType(
        ModelType(RequirementGroup, required=True),
        required=True,
        min_size=1,
        validators=[validate_requirement_groups],
    )

    def validate_relatedItem(self, data, value):
        if value:
            if get_first_revision_date(get_tender(), default=get_now()) < PQ_MULTI_PROFILE_FROM:
                raise ValidationError("Rogue field.")

    def validate_relatesTo(self, data, value):
        if value:
            if get_first_revision_date(get_tender(), default=get_now()) < PQ_MULTI_PROFILE_FROM:
                raise ValidationError("Rogue field.")


def validate_criterion_related_items(data, criterion_list):
    if criterion_list:
        multi_profile_released = get_first_revision_date(get_tender(), default=get_now()) > PQ_MULTI_PROFILE_FROM
        item_ids = {i["id"] for i in data["items"]}
        for criterion in criterion_list:
            related_item = criterion.get("relatedItem")

            if not multi_profile_released and related_item:
                raise ValidationError("Rogue field.")

            if not related_item and data.get("relatesTo"):
                raise ValidationError("This field is required.")

            if related_item is not None and related_item not in item_ids:
                raise ValidationError("relatedItem should be one of items")
