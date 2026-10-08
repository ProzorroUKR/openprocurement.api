from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin
from openprocurement.tender.open.procedure.state.tender_details import (
    AboveThresholdEUTenderDetailsState,
    AboveThresholdTenderDetailsState,
    AboveThresholdUATenderDetailsState,
    BelowThresholdTenderDetailsState,
    COLongTenderDetailsState,
    COShortTenderDetailsState,
    RFPTenderDetailsState,
    SimpleDefenseTenderDetailsState,
)


class AboveThresholdCriterionState(CriterionStateMixin, AboveThresholdTenderDetailsState):
    pass


class AboveThresholdUACriterionState(CriterionStateMixin, AboveThresholdUATenderDetailsState):
    pass


class AboveThresholdEUCriterionState(CriterionStateMixin, AboveThresholdEUTenderDetailsState):
    pass


class COShortCriterionState(CriterionStateMixin, COShortTenderDetailsState):
    pass


class COLongCriterionState(CriterionStateMixin, COLongTenderDetailsState):
    pass


class BelowThresholdCriterionState(CriterionStateMixin, BelowThresholdTenderDetailsState):
    pass


class RFPCriterionState(CriterionStateMixin, RFPTenderDetailsState):
    pass


class SimpleDefenseCriterionState(CriterionStateMixin, SimpleDefenseTenderDetailsState):
    pass
