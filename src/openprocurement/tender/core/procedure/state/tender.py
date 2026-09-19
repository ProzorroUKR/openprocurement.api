from logging import getLogger

from openprocurement.api.constants import (
    KIND_PROCUREMENT_METHOD_TYPE_MAPPING,
    WORKING_DAYS,
)
from openprocurement.api.constants_env import PROCUREMENT_ENTITY_KIND_VALIDATION_FROM
from openprocurement.api.context import get_request, get_request_now
from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.procedure.utils import is_item_owner
from openprocurement.api.utils import raise_operation_error
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
from openprocurement.tender.core.procedure.utils import tender_created_after

LOGGER = getLogger(__name__)


class BlockComplaintMixing:
    # complaints (by type) that block awards/contracts/cancellations processing
    block_complaint_status = {
        "complaint": ("pending", "accepted", "satisfied", "stopping"),
    }
    # complaints (by type) that block tendering end: tender can't proceed from active.tendering
    # until it has unanswered claims or unresolved complaints
    block_tender_complaint_status = {
        "complaint": ("pending", "accepted", "satisfied", "stopping"),
        "claim": ("claim",),
    }

    @classmethod
    def is_blocking_complaint(cls, complaint, block_statuses=None):
        if block_statuses is None:
            block_statuses = cls.block_complaint_status
        # legacy complaints may have no type stored, they are complaints (not claims)
        complaint_type = complaint.get("type", "complaint")
        return complaint.get("status") in block_statuses.get(complaint_type, ())

    @classmethod
    def is_blocking_tender_complaint(cls, complaint):
        return cls.is_blocking_complaint(complaint, block_statuses=cls.block_tender_complaint_status)


class TenderState(
    ShouldStartAfterMixing,
    CancellationBlockMixing,
    TenderStateAwardingMixing,
    ChronographEventsMixing,
    ReviewRequestBlockMixin,
    TenderCriterionMixin,
    BlockComplaintMixing,
    BaseState,
):
    active_bid_statuses = ("active", "pending")
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

    def on_post(self, data):
        self._validate_procurement_entity_kind(data)
        super().on_post(data)

    def on_patch(self, before, after):
        if before.get("procuringEntity") != after.get("procuringEntity"):
            self._validate_procurement_entity_kind(after)
        super().on_patch(before, after)

    def always(self, data):
        super().always(data)
        self.calc_auction_periods(data)
        self.update_next_check(data)  # next_check should be after calc_auction_periods
        self.calc_tender_values(data)

    def _validate_procurement_entity_kind(self, data):
        if tender_created_after(PROCUREMENT_ENTITY_KIND_VALIDATION_FROM):
            proc_method_type = data.get("procurementMethodType")
            proc_entity_kind = data.get("procuringEntity", {}).get("kind")
            if proc_entity_kind not in KIND_PROCUREMENT_METHOD_TYPE_MAPPING.get(proc_method_type, []):
                raise_operation_error(
                    get_request(),
                    f"Procedure publishing with method type {proc_method_type} is not allowed for procuringEntity.kind {proc_entity_kind}",
                    status=422,
                    name="procuringEntity",
                )

    # priceQuotation: bids are never invalidated by tender changes
    bids_invalidation_enabled = True

    def invalidate_bids_data(self, tender):
        if not self.bids_invalidation_enabled:
            return
        if is_item_owner(get_request(), tender) and tender.get("status") == "active.tendering":
            self.set_bids_invalidation_date(tender)
            for bid in tender.get("bids", ""):
                if bid.get("status") not in ("deleted", "draft"):
                    bid["status"] = "invalid"

    def set_bids_invalidation_date(self, tender):
        if not self.bids_invalidation_enabled:
            return
        if "enquiryPeriod" in tender:
            tender["enquiryPeriod"]["invalidationDate"] = get_request_now().isoformat()
