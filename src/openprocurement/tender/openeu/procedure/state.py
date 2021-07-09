# -*- coding: utf-8 -*-
from openprocurement.api.utils import error_handler
from openprocurement.tender.core.procedure.context import get_now
from openprocurement.tender.core.procedure.state import BidState as BaseBidState


class BidState(BaseBidState):

    def __init__(self, request, data):
        self.request = request
        self._data = data
        self.now = get_now().isoformat()

    def status_up(self, before, after):
        assert before != after, "Statuses must be different"
        # this logic moved here from validate_update_bid_status validator
        # if request.authenticated_role != "Administrator":
        if after not in ("pending", "active"):
            self.request.errors.add("body", "bid", "Can't update bid to ({}) status".format(after))
            self.request.errors.status = 403
            raise error_handler(self.request)

