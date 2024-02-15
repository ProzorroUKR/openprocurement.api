from operator import itemgetter

from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.openeu.procedure.models.award import Award


class BaseOpenEUTenderState(TenderState):
    award_class = Award
    active_bid_statuses = ("active", "pending")
    block_complaint_status = ("pending", "accepted", "satisfied", "stopping")

    def invalidate_bids_data(self, tender):
        tender["enquiryPeriod"]["invalidationDate"] = get_now().isoformat()
        for bid in tender.get("bids", ""):
            if bid.get("status") not in ("deleted", "draft"):
                bid["status"] = "invalid"
