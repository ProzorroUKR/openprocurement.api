from openprocurement.tender.arma.procedure.state.tender_details import (
    ComplexAssetTenderDetailsState,
    SimpleAssetTenderDetailsState,
)
from openprocurement.tender.core.procedure.state.criterion_rg import RequirementGroupStateMixin


class ComplexAssetRequirementGroupState(RequirementGroupStateMixin, ComplexAssetTenderDetailsState):
    pass


class SimpleAssetRequirementGroupState(RequirementGroupStateMixin, SimpleAssetTenderDetailsState):
    pass
