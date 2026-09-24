from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.core.procedure.state.chronograph import (
    IgnoredClaimMixin,
)
from openprocurement.tender.core.procedure.state.tender import TenderState


class RFPIgnoredClaimMixin(IgnoredClaimMixin):
    tender_claims_events = True
    tendering_end_waits_for_unanswered = False


class RFPTenderState(RFPIgnoredClaimMixin, TenderState):
    award_class = Award

    generate_award_milestones = False
