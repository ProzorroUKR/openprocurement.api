from openprocurement.tender.openeu.procedure.state.bid import OpenEUBidState
from openprocurement.tender.openua.procedure.state.bid import OpenUABidState


class CDStage2EUBidState(OpenEUBidState):
    bid_post_shortlisted_firms_check = True


class CDStage2UABidState(OpenUABidState):
    bid_post_shortlisted_firms_check = True
