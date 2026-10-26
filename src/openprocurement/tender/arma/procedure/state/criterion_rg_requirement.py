from openprocurement.tender.arma.procedure.state.tender_details import (
    ComplexAssetTenderDetailsState,
    SimpleAssetTenderDetailsState,
)
from openprocurement.tender.core.procedure.state.criterion_rg_requirement import RequirementStateMixin


class ComplexAssetRequirementState(RequirementStateMixin, ComplexAssetTenderDetailsState):
    pass


class SimpleAssetRequirementState(RequirementStateMixin, SimpleAssetTenderDetailsState):
    pass
