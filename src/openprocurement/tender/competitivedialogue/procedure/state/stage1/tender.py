from openprocurement.tender.openeu.procedure.state.tender import BaseOpenEUTenderState


class CDStage1TenderState(BaseOpenEUTenderState):
    pre_qualification_stand_still_next_status = "active.stage2.pending"
    # first stage don't need auctionPeriod
    # this actually doesn't work, because non-refactored endpoints add auctionPeriod
    # I'm going to add "auctionPeriod" to private fields in serializer, until we update all the code
    tender_auction_periods = False
