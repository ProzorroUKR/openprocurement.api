from schematics.types import StringType, MD5Type
from schematics.types.compound import ModelType
from schematics.exceptions import ValidationError
from schematics.transforms import blacklist
from openprocurement.api.models import schematics_default_role, schematics_embedded_role, ListType, Model
from openprocurement.api.utils import get_now, get_first_revision_date
from openprocurement.tender.pricequotation.models.requirement import Requirement, ValidateIdMixing
from openprocurement.tender.pricequotation.validation import validate_requirement_groups
from openprocurement.tender.core.models import get_tender
from openprocurement.api.constants import PQ_MULTI_PROFILE_FROM


class RequirementGroup(ValidateIdMixing, Model):
    class Options:
        namespace = "RequirementGroup"
        roles = {
            "create": blacklist(),
            "edit_draft": blacklist(),
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
        }
    description = StringType(required=True)
    requirements = ListType(ModelType(Requirement, required=True), default=list)


class Criterion(ValidateIdMixing, Model):
    class Options:
        namespace = "Criterion"
        roles = {
            "create": blacklist(),
            "edit_draft": blacklist(),
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
        }

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
