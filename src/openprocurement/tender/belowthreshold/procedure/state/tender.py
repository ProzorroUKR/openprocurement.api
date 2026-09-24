from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.core.procedure.state.chronograph import (
    IgnoredClaimMixin,
)
from openprocurement.tender.core.procedure.state.tender import TenderState


class BelowThresholdIgnoredClaimMixin(IgnoredClaimMixin):
    tender_claims_events = True
    tendering_end_waits_for_unanswered = False


class BelowThresholdTenderState(BelowThresholdIgnoredClaimMixin, TenderState):
    award_class = Award

    generate_award_milestones = False
