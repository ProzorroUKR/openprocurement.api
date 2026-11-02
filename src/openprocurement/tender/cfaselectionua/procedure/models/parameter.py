from openprocurement.api.procedure.types import StringDecimalType
from openprocurement.tender.core.procedure.models.parameter import (
    Parameter,
    PatchParameter,
)


class CFASelectionParameter(Parameter):
    value = StringDecimalType(required=True)


class CFASelectionPatchParameter(PatchParameter):
    value = StringDecimalType()
