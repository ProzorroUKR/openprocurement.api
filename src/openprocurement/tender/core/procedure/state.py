# -*- coding: utf-8 -*-
from openprocurement.api.utils import error_handler, handle_data_exceptions
from openprocurement.tender.core.procedure.context import get_now


class BidState:

    def __init__(self, request, data):
        self.request = request
        self._data = data
        self.now = get_now().isoformat()

    def status_up(self, before, after):
        assert before != after, "Statuses must be different"
        # this logic moved here from validate_update_bid_status validator
        # if request.authenticated_role != "Administrator":
        if after != "active":
            self.request.errors.add("body", "bid", "Can't update bid to ({}) status".format(after))
            self.request.errors.status = 403
            raise error_handler(self.request)

    def on_post(self):
        self._data["date"] = self.now

        for lot_value in self._data.get("lotValues", ""):
            lot_value["date"] = self.now

    def on_patch(self, before, after):
        # if value.amount is going to be changed -> update "date"
        amount_before = (before.get("value") or {}).get("amount")
        amount_after = (after.get("value") or {}).get("amount")
        if amount_before != amount_after:
            after["date"] = self.now

        # the same as above, for lots
        for after_lot in after.get("lotValues", ""):
            for before_lot in before.get("lotValues", ""):
                if before_lot["relatedLot"] == after_lot["relatedLot"]:
                    if float(before_lot["value"]["amount"]) != after_lot["value"]["amount"]:
                        after_lot["date"] = self.now
                    break
            else:  # lotValue has been just added
                after_lot["date"] = self.now

        # if status has changed, we should take additional actions according to procedure
        if "status" in after and before["status"] != after["status"]:
            self.status_up(before["status"], after["status"])
