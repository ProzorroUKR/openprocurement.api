from openprocurement.tender.core.procedure.state.criterion_rg import RequirementGroupStateMixin
from openprocurement.tender.limited.procedure.state.tender_details import (
    NegotiationQuickTenderDetailsState,
    NegotiationTenderDetailsState,
    ReportingTenderDetailsState,
)


class ReportingRequirementGroupState(RequirementGroupStateMixin, ReportingTenderDetailsState):
    pass


class NegotiationRequirementGroupState(RequirementGroupStateMixin, NegotiationTenderDetailsState):
    pass


class NegotiationQuickRequirementGroupState(RequirementGroupStateMixin, NegotiationQuickTenderDetailsState):
    pass
