from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.core.procedure.state.chronograph import (
    IgnoredClaimMixing as BaseIgnoredClaimMixing,
)
from openprocurement.tender.core.procedure.state.tender import TenderState


class IgnoredClaimMixing(BaseIgnoredClaimMixing):
    tender_claims_events = True
    tendering_end_waits_for_unanswered = False


class BelowThresholdTenderState(IgnoredClaimMixing, TenderState):
    award_class = Award
    block_complaint_status = ()
    generate_award_milestones = False
