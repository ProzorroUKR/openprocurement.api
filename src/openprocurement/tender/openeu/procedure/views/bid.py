from openprocurement.api.auth import ACCR_4
from openprocurement.api.utils import json_view, context_unpack
from openprocurement.tender.core.procedure.views.bid import TenderBidResource
from openprocurement.tender.core.procedure.models.bid import filter_administrator_bid_update
from openprocurement.tender.openeu.procedure.models.bid import PostBid, PatchBid, Bid
from openprocurement.tender.core.procedure.state.bid import BidState
from openprocurement.tender.core.procedure.utils import save_tender
from openprocurement.tender.core.procedure.serializers.bid import BidSerializer
from openprocurement.tender.core.procedure.validation import (
    validate_update_deleted_bid,
    validate_bid_operation_period,
    validate_bid_operation_not_in_tendering,
    validate_view_bids,
)
from openprocurement.api.procedure.validation import (
    validate_patch_data,
    validate_input_data,
    validate_data_documents,
    validate_item_owner, unless_item_owner, unless_administrator, validate_accreditation_level,
)
from cornice.resource import resource
from logging import getLogger

LOGGER = getLogger(__name__)


@resource(
    name="aboveThresholdEU:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender EU bids",
)
class TenderBidResource(TenderBidResource):

    state_class = BidState
    serializer_class = BidSerializer

    @json_view(
        permission="view_tender",
        validators=(
            validate_view_bids,
        )
    )
    def collection_get(self):
        return super().collection_get()

    @json_view(
        permission="view_tender",
        validators=(
            unless_item_owner(
                validate_view_bids,
                item_name="bid"
            ),
        )
    )
    def get(self):
        return super().get()

    @json_view(
        content_type="application/json",
        permission="create_bid",
        validators=(
            validate_accreditation_level(
                levels=(ACCR_4,),
                item="bid",
                operation="creation",
            ),
            validate_bid_operation_not_in_tendering,
            validate_bid_operation_period,
            validate_input_data(PostBid),
            validate_data_documents(route_key="bid_id", uid_key="id"),
        ),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        permission="edit_bid",
        validators=(
            unless_administrator(validate_item_owner("bid")),
            validate_update_deleted_bid,

            validate_input_data(PatchBid, filters=(filter_administrator_bid_update,), none_means_remove=True),
            validate_patch_data(Bid, item_name="bid"),

            validate_bid_operation_not_in_tendering,
            validate_bid_operation_period,
        ),
    )
    def patch(self):
        return super().patch()

    @json_view(
        permission="edit_bid",
        validators=(
            validate_item_owner("bid"),
            validate_bid_operation_not_in_tendering,
            validate_bid_operation_period,
        )
    )
    def delete(self):
        bid = self.request.validated["bid"]
        bid["status"] = "deleted"
        if bid.get("lotValues"):
            bid["lotValues"] = []
        if save_tender(self.request, modified=False):
            self.LOGGER.info(
                "Deleted tender bid {}".format(bid["id"]),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_bid_delete"}),
            )
            return {"data": self.serializer_class(bid).data}
