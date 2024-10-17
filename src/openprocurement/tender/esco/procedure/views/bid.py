from logging import getLogger

from cornice.resource import resource

from openprocurement.api.auth import ACCR_4
from openprocurement.api.procedure.validation import (
    unless_administrator,
    unless_item_owner,
    validate_accreditation_level,
    validate_data_documents,
    validate_input_data,
    validate_item_owner,
    validate_patch_data_simple,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.models.bid import (
    filter_administrator_bid_update,
)
from openprocurement.tender.core.procedure.state.bid import BidState
from openprocurement.tender.core.procedure.validation import (
    validate_bid_operation_not_in_tendering,
    validate_bid_operation_period,
    validate_update_deleted_bid,
    validate_view_bids,
)
from openprocurement.tender.core.utils import context_view
from openprocurement.tender.esco.procedure.models.bid import Bid, PatchBid, PostBid
from openprocurement.tender.esco.procedure.serializers.bid import BidSerializer
from openprocurement.tender.esco.procedure.serializers.tender import (
    ESCOTenderSerializer,
)
from openprocurement.tender.openeu.procedure.views.bid import OpenEUTenderBidResource

LOGGER = getLogger(__name__)


@resource(
    name="esco:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType="esco",
    description="Tender ESCO bids",
)
class ESCOTenderBidResource(OpenEUTenderBidResource):
    state_class = BidState
    serializer_class = BidSerializer

    @json_view(
        permission="view_tender",
        validators=(validate_view_bids,),
    )
    def collection_get(self):
        return super().collection_get()

    @json_view(
        permission="view_tender",
        validators=(
            unless_item_owner(
                validate_view_bids,
                item_name="bid",
            ),
        ),
    )
    @context_view(
        objs={
            "tender": ESCOTenderSerializer,
        }
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
            validate_input_data(
                PatchBid,
                filters=(filter_administrator_bid_update,),
                none_means_remove=True,
            ),
            validate_patch_data_simple(Bid, item_name="bid"),
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
        ),
    )
    def delete(self):
        return super().delete()
