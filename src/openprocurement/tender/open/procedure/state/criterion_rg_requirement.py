from openprocurement.tender.core.procedure.state.criterion_rg_requirement import RequirementStateMixin
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


class AboveThresholdRequirementState(RequirementStateMixin, AboveThresholdTenderDetailsState):
    pass


class AboveThresholdUARequirementState(RequirementStateMixin, AboveThresholdUATenderDetailsState):
    pass


class AboveThresholdEURequirementState(RequirementStateMixin, AboveThresholdEUTenderDetailsState):
    pass


class COShortRequirementState(RequirementStateMixin, COShortTenderDetailsState):
    pass


class COLongRequirementState(RequirementStateMixin, COLongTenderDetailsState):
    pass


class BelowThresholdRequirementState(RequirementStateMixin, BelowThresholdTenderDetailsState):
    pass


class RFPRequirementState(RequirementStateMixin, RFPTenderDetailsState):
    pass


class SimpleDefenseRequirementState(RequirementStateMixin, SimpleDefenseTenderDetailsState):
    pass
