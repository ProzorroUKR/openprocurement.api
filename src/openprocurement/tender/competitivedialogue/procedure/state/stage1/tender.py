from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.openeu.procedure.state.tender import BaseOpenEUTenderState


class Stage1TenderState(BaseOpenEUTenderState):

    min_bids_number = 3

    def pre_qualification_stand_still_ends_handler(self, tender):
        handler = self.get_change_tender_status_handler("active.stage2.pending")
        handler(tender)

        self.check_bids_number(tender)

    def validate_minimal_step(self, data, before=None):
        if data.get("minimalStep") is None:
            raise_operation_error(
                self.request,
                ["This field is required."],
                status=422,
                location="body",
                name="minimalStep",
            )

    # first stage don't need auctionPeriod
    # this actually doesn't work, because non-refactored endpoints add auctionPeriod
    # I'm going to add "auctionPeriod" to private fields in serializer, until we update all the code
    def calc_auction_periods(self, tender):
        pass

    # "active.stage2.waiting"
