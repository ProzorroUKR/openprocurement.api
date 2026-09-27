from openprocurement.tender.core.procedure.state.criterion_rg_requirement_evidence import EligibleEvidenceStateMixin
from openprocurement.tender.limited.procedure.state.tender_details import (
    NegotiationQuickTenderDetailsState,
    NegotiationTenderDetailsState,
    ReportingTenderDetailsState,
)


class ReportingEligibleEvidenceState(EligibleEvidenceStateMixin, ReportingTenderDetailsState):
    pass


class NegotiationEligibleEvidenceState(EligibleEvidenceStateMixin, NegotiationTenderDetailsState):
    pass


class NegotiationQuickEligibleEvidenceState(EligibleEvidenceStateMixin, NegotiationQuickTenderDetailsState):
    pass
