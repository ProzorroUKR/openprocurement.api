from openprocurement.tender.core.procedure.state.bid import BidState as BaseBidState


class BidState(BaseBidState):
    self_eligible_required = False
    bid_agreement_from_tender = True
    bid_agreement_check_on_patch = True
