from openprocurement.tender.core.procedure.state.criterion_rg import RequirementGroupStateMixin
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


class AboveThresholdRequirementGroupState(RequirementGroupStateMixin, AboveThresholdTenderDetailsState):
    pass


class AboveThresholdUARequirementGroupState(RequirementGroupStateMixin, AboveThresholdUATenderDetailsState):
    pass


class AboveThresholdEURequirementGroupState(RequirementGroupStateMixin, AboveThresholdEUTenderDetailsState):
    pass


class COShortRequirementGroupState(RequirementGroupStateMixin, COShortTenderDetailsState):
    pass


class COLongRequirementGroupState(RequirementGroupStateMixin, COLongTenderDetailsState):
    pass


class BelowThresholdRequirementGroupState(RequirementGroupStateMixin, BelowThresholdTenderDetailsState):
    pass


class RFPRequirementGroupState(RequirementGroupStateMixin, RFPTenderDetailsState):
    pass


class SimpleDefenseRequirementGroupState(RequirementGroupStateMixin, SimpleDefenseTenderDetailsState):
    pass
