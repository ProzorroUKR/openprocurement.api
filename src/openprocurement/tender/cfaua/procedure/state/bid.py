from openprocurement.tender.core.procedure.state.bid import BidState as BaseBidState
from openprocurement.api.utils import error_handler


class BidState(BaseBidState):
    def status_up(self, before, after, data):
        assert before != after, "Statuses must be different"
        # this logic moved here from validate_update_bid_status validator
        # if request.authenticated_role != "Administrator":
        if after != "pending":
            self.request.errors.add("body", "bid", "Can't update bid to ({}) status".format(after))
            self.request.errors.status = 403
            raise error_handler(self.request)

