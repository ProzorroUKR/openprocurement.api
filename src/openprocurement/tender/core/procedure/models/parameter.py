from openprocurement.api.procedure.errors import ValidationError
from openprocurement.api.procedure.models.base import Model


class Parameter(Model):
    code: str
    value: float


class PatchParameter(Parameter):
    code: str | None = None
    value: float | None = None


def validate_cfa_selection_parameter_contracts(features, contracts):
    options = {f.code: {e.value for e in f.enum} for f in features or []}
    for contract in contracts or []:
        for param in contract.parameters or []:
            if param.code not in options:
                raise ValidationError("code should be one of feature code.")

            if param.value not in options[param.code]:
                raise ValidationError("value should be one of feature value.")
