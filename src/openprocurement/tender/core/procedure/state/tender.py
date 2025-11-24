from logging import getLogger

from openprocurement.api.constants import WORKING_DAYS
from openprocurement.api.context import get_request, get_request_now
from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.procedure.utils import is_item_owner
from openprocurement.tender.core.procedure.awarding import TenderStateAwardingMixing
from openprocurement.tender.core.procedure.cancelling import CancellationBlockMixing
from openprocurement.tender.core.procedure.criteria import TenderCriterionMixin
from openprocurement.tender.core.procedure.reviewing_request import (
    ReviewRequestBlockMixin,
)
from openprocurement.tender.core.procedure.state.auction import ShouldStartAfterMixing
from openprocurement.tender.core.procedure.state.chronograph import (
    ChronographEventsMixing,
)
from openprocurement.tender.core.procedure.utils import dt_from_iso

LOGGER = getLogger(__name__)


class TenderState(
    ShouldStartAfterMixing,
    CancellationBlockMixing,
    TenderStateAwardingMixing,
    ChronographEventsMixing,
    ReviewRequestBlockMixin,
    TenderCriterionMixin,
    BaseState,
):
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
    terminated_statuses = (
        "complete",
        "unsuccessful",
        "cancelled",
        "draft.unsuccessful",
    )
    calendar = WORKING_DAYS

    def status_up(self, before, after, data):
        super().status_up(before, after, data)
        data["date"] = get_request_now().isoformat()

        # TODO: redesign auction planning
        if after in self.unsuccessful_statuses:
            self.remove_all_auction_periods(data)

    def always(self, data):
        super().always(data)
        tender_before = get_request().validated["tender_src"]
        if (tender_period_end_date := data.get("tenderPeriod", {}).get("endDate")) and (
            data["status"] == "draft"
            or data["tenderPeriod"]["endDate"] != tender_before.get("tenderPeriod", {}).get("endDate")
        ):
            self.calc_qualification_period(data, dt_from_iso(tender_period_end_date))
        self.calc_auction_periods(data)
        self.update_next_check(data)  # next_check should be after calc_auction_periods
        self.calc_tender_values(data)

    def invalidate_bids_data(self, tender):
        if is_item_owner(get_request(), tender) and tender.get("status") == "active.tendering":
            self.set_bids_invalidation_date(tender)
            for bid in tender.get("bids", ""):
                if bid.get("status") not in ("deleted", "draft"):
                    bid["status"] = "invalid"

    @staticmethod
    def set_bids_invalidation_date(tender):
        if "enquiryPeriod" in tender:
            tender["enquiryPeriod"]["invalidationDate"] = get_request_now().isoformat()
