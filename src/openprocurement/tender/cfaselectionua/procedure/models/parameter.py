from openprocurement.api.procedure.types import StringDecimalType
from openprocurement.tender.core.procedure.models.parameter import (
    Parameter,
    PatchParameter,
    validate_cfa_selection_parameter_value,
)


class CFASelectionParameter(Parameter):
    value = StringDecimalType(required=True)

    def validate_value(self, data, value):
        validate_cfa_selection_parameter_value(data, value)


class CFASelectionPatchParameter(PatchParameter):
    value = StringDecimalType()

    def validate_value(self, data, value):
        return value
