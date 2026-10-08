from openprocurement.tender.core.procedure.state.criterion_rg_requirement import RequirementStateMixin
from openprocurement.tender.limited.procedure.state.tender_details import (
    NegotiationQuickTenderDetailsState,
    NegotiationTenderDetailsState,
    ReportingTenderDetailsState,
)


class ReportingRequirementState(RequirementStateMixin, ReportingTenderDetailsState):
    pass


class NegotiationRequirementState(RequirementStateMixin, NegotiationTenderDetailsState):
    pass


class NegotiationQuickRequirementState(RequirementStateMixin, NegotiationQuickTenderDetailsState):
    pass
