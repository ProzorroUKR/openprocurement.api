from openprocurement.tender.core.procedure.state.criterion_rq_requirement_evidence import (
    EligibleEvidenceStateMixin,
)
from openprocurement.tender.open.procedure.state.tender import (
    AboveThresholdTenderState,
    AboveThresholdUATenderState,
    COTenderState,
)


class AboveThresholdEligibleEvidenceState(EligibleEvidenceStateMixin, AboveThresholdTenderState):
    pass


class AboveThresholdUAEligibleEvidenceState(EligibleEvidenceStateMixin, AboveThresholdUATenderState):
    pass


class COEligibleEvidenceState(EligibleEvidenceStateMixin, COTenderState):
    pass
