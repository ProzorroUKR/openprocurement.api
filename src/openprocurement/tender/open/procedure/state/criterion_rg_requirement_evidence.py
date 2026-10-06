from openprocurement.tender.core.procedure.state.criterion_rg_requirement_evidence import EligibleEvidenceStateMixin
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


class AboveThresholdEligibleEvidenceState(EligibleEvidenceStateMixin, AboveThresholdTenderDetailsState):
    pass


class AboveThresholdUAEligibleEvidenceState(EligibleEvidenceStateMixin, AboveThresholdUATenderDetailsState):
    pass


class AboveThresholdEUEligibleEvidenceState(EligibleEvidenceStateMixin, AboveThresholdEUTenderDetailsState):
    pass


class COShortEligibleEvidenceState(EligibleEvidenceStateMixin, COShortTenderDetailsState):
    pass


class COLongEligibleEvidenceState(EligibleEvidenceStateMixin, COLongTenderDetailsState):
    pass


class BelowThresholdEligibleEvidenceState(EligibleEvidenceStateMixin, BelowThresholdTenderDetailsState):
    pass


class RFPEligibleEvidenceState(EligibleEvidenceStateMixin, RFPTenderDetailsState):
    pass


class SimpleDefenseEligibleEvidenceState(EligibleEvidenceStateMixin, SimpleDefenseTenderDetailsState):
    pass
