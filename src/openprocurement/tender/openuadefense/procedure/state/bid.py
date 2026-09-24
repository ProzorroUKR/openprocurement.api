from openprocurement.tender.core.procedure.state.bid import BidState


class DefenseBidState(BidState):
    self_eligible_rogue_after_ecriteria = False
    requirement_responses_allowed = False
