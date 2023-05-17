# -*- coding: utf-8 -*-
from openprocurement.tender.core.procedure.state.bid import BidState as BaseBidState


class Stage1BidState(BaseBidState):

    def on_patch(self, before, after):
        self.validate_status_change(after)
        self.validate_lot_values_statuses(after)
        # Removing logic with if value.amount is going to be changed -> update "date"

        # if status has changed, we should take additional actions according to procedure
        if "status" in after and before["status"] != after["status"]:
            self.status_up(before["status"], after["status"], after)
