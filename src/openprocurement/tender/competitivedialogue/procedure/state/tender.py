from openprocurement.tender.openeu.procedure.state.tender import OpenEUTenderState


class Stage1EUTenderState(OpenEUTenderState):

    min_bids_number = 3

    def pre_qualification_stand_still_ends_handler(self, tender):
        handler = self.get_change_tender_status_handler("active.stage2.pending")
        handler(tender)

        self.check_bids_number(tender)
