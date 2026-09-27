from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin
from openprocurement.tender.limited.procedure.state.tender_details import (
    NegotiationQuickTenderDetailsState,
    NegotiationTenderDetailsState,
    ReportingTenderDetailsState,
)


class ReportingCriterionState(CriterionStateMixin, ReportingTenderDetailsState):
    pass


class NegotiationCriterionState(CriterionStateMixin, NegotiationTenderDetailsState):
    pass


class NegotiationQuickCriterionState(CriterionStateMixin, NegotiationQuickTenderDetailsState):
    pass
