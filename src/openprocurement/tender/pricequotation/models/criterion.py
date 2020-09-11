from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.models import ListType, Model
from openprocurement.tender.pricequotation.models.requirement import Requirement
from openprocurement.tender.core.validation import validate_requirement_groups


class RequirementGroup(Model):
    id = StringType(required=True)
    description = StringType(required=True)
    requirements = ListType(ModelType(Requirement, required=True), default=list())


class Criterion(Model):
    id = StringType(required=True)
    title = StringType(required=True)
    description = StringType(required=True)
    requirementGroups = ListType(ModelType(RequirementGroup),
                                 required=True,
                                 validators=[validate_requirement_groups])
