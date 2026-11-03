from schematics.exceptions import ValidationError
from schematics.types import FloatType, StringType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import DecimalType


class Parameter(Model):
    code = StringType(required=True)
    value = FloatType(required=True)


class PatchParameter(Parameter):
    code = StringType()
    value = FloatType()


def validate_cfa_selection_parameter_contracts(features, contracts):
    options = {f.code: {e.value for e in f.enum} for f in features or []}
    for contract in contracts or []:
        for param in contract.parameters or []:
            if param.code not in options:
                raise ValidationError("code should be one of feature code.")

            if param.value not in options[param.code]:
                raise ValidationError("value should be one of feature value.")


class AgreementContractParameter(Model):
    code = StringType(required=True)
    value = DecimalType(required=True)
