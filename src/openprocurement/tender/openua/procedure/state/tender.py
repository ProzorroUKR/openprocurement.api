from openprocurement.api.context import get_request_now
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.openua.procedure.models.award import Award


class OpenUATenderState(TenderState):
    block_complaint_status = ("pending", "accepted", "satisfied", "stopping")
    award_class = Award

    @classmethod
    def invalidate_bids_data(cls, tender):
        tender["enquiryPeriod"]["invalidationDate"] = get_request_now().isoformat()
        for bid in tender.get("bids", ""):
            if bid.get("status") not in ("deleted", "draft"):
                bid["status"] = "invalid"
