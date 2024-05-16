from logging import getLogger

from openprocurement.api.context import get_now
from openprocurement.api.procedure.state.base import BaseState
from openprocurement.tender.core.procedure.awarding import TenderStateAwardingMixing
from openprocurement.tender.core.procedure.cancelling import CancellationBlockMixing
from openprocurement.tender.core.procedure.models.contract import Contract
from openprocurement.tender.core.procedure.reviewing_request import (
    ReviewRequestBlockMixin,
)
from openprocurement.tender.core.procedure.state.auction import ShouldStartAfterMixing
from openprocurement.tender.core.procedure.state.chronograph import (
    ChronographEventsMixing,
)

LOGGER = getLogger(__name__)


class TenderState(
    ShouldStartAfterMixing,
    CancellationBlockMixing,
    TenderStateAwardingMixing,
    ChronographEventsMixing,
    ReviewRequestBlockMixin,
    BaseState,
):
    contract_model = Contract
    active_bid_statuses = ("active", "pending")
    block_complaint_status = ("answered", "pending")
    block_tender_complaint_status = (
        "claim",
        "pending",
        "accepted",
        "satisfied",
        "stopping",
    )  # tender can't proceed to "active.auction" until has a tender.complaints in one of statuses
    unsuccessful_statuses = ("cancelled", "unsuccessful")
    terminated_statuses = ("complete", "unsuccessful", "cancelled", "draft.unsuccessful")

    def status_up(self, before, after, data):
        super().status_up(before, after, data)
        data["date"] = get_now().isoformat()

        # TODO: redesign auction planning
        if after in self.unsuccessful_statuses:
            self.remove_all_auction_periods(data)

    def always(self, data):
        super().always(data)
        self.update_next_check(data)
        self.calc_auction_periods(data)
        self.calc_tender_values(data)
