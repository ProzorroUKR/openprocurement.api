from openprocurement.tender.arma.procedure.state.tender_details import (
    ComplexAssetTenderDetailsState,
    SimpleAssetTenderDetailsState,
)
from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin


class ComplexAssetCriterionState(CriterionStateMixin, ComplexAssetTenderDetailsState):
    pass


class SimpleAssetCriterionState(CriterionStateMixin, SimpleAssetTenderDetailsState):
    pass
