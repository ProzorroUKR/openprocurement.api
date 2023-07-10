from operator import itemgetter

from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.api.context import get_now
from openprocurement.tender.openeu.procedure.models.award import Award
from openprocurement.tender.openeu.utils import is_procedure_restricted


class BaseOpenEUTenderState(TenderState):
    award_class = Award
    active_bid_statuses = ("active", "pending")
    block_complaint_status = ("pending", "accepted", "satisfied", "stopping")

    def invalidate_bids_data(self, tender):
        tender["enquiryPeriod"]["invalidationDate"] = get_now().isoformat()
        for bid in tender.get("bids", ""):
            if bid.get("status") not in ("deleted", "draft"):
                bid["status"] = "invalid"


class OpenEUTenderState(BaseOpenEUTenderState):
    def tendering_end_handler(self, tender):
        if is_procedure_restricted(tender):
            self.min_bids_number = tender.get("preQualificationMinBidsNumber", 4)
        super().tendering_end_handler(tender)

    def pre_qualification_stand_still_ends_handler(self, tender):
        if is_procedure_restricted(tender):
            self.min_bids_number = tender.get("preQualificationMinBidsNumber", 4)

        super().pre_qualification_stand_still_ends_handler(tender)

        if is_procedure_restricted(tender):
            self.qualification_bids_by_rating(tender)

    def qualification_bids_by_rating(self, tender):
        self.min_bids_number = tender.get("preQualificationMinBidsNumber", 4)

        bid_limit = tender.get("preQualificationFeaturesRatingBidLimit")
        bids = tender.get("bids", "")

        if not bid_limit:
            return

        bids_with_sum_params = [
            (bid, sum(param["value"] for param in bid.get("parameters", "")))
            for bid in bids
        ]
        sorted_bids = sorted(bids_with_sum_params, key=itemgetter(1), reverse=True)

        for bid, _ in sorted_bids[bid_limit:]:
            bid["status"] = "unsuccessful"
