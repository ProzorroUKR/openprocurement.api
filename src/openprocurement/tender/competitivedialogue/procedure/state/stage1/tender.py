from openprocurement.tender.openeu.procedure.state.tender import BaseOpenEUTenderState


class Stage1TenderState(BaseOpenEUTenderState):

    def pre_qualification_stand_still_ends_handler(self, tender):
        handler = self.get_change_tender_status_handler("active.stage2.pending")
        handler(tender)

        self.check_bids_number(tender)

    # first stage don't need auctionPeriod
    # this actually doesn't work, because non-refactored endpoints add auctionPeriod
    # I'm going to add "auctionPeriod" to private fields in serializer, until we update all the code
    def calc_auction_periods(self, tender):
        pass

    # "active.stage2.waiting"
