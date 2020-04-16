from openprocurement.api.models import ListType, Model
from openprocurement.tender.pricequotation.models.requirement import (RequirementBoolean, RequirementDateTime,
                                                                      RequirementInteger, RequirementNumber,
                                                                      RequirementString)
from openprocurement.tender.pricequotation.utils import get_requirement_class
from schematics.types import StringType
from schematics.types.compound import ModelType, PolyModelType


class RequirementGroup(Model):
    id = StringType(required=True)
    description = StringType(required=True)
    requirements = ListType(PolyModelType((RequirementInteger,
                                           RequirementDateTime,
                                           RequirementString,
                                           RequirementNumber,
                                           RequirementBoolean), claim_function=get_requirement_class), default=list())


class Criterion(Model):
    id = StringType(required=True)
    code = StringType(required=True)
    title = StringType(required=True)
    description = StringType(required=True)
    requirementGroups = ListType(ModelType(RequirementGroup), required=True)
