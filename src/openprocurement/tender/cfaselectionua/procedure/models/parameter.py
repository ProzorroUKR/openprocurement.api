from openprocurement.api.procedure.types import (
    StringDecimal,
)
from openprocurement.tender.core.procedure.models.parameter import (
    Parameter,
    PatchParameter,
)


class CFASelectionParameter(Parameter):
    value: StringDecimal


class CFASelectionPatchParameter(PatchParameter):
    value: StringDecimal | None = None
