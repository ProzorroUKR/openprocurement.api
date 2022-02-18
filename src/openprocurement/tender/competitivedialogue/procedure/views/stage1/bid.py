from openprocurement.api.utils import json_view
from openprocurement.tender.openeu.procedure.views.bid import TenderBidResource
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.core.procedure.models.bid import filter_administrator_bid_update
from openprocurement.tender.competitivedialogue.procedure.models.bid import PostBid, PatchBid, Bid
from openprocurement.tender.competitivedialogue.procedure.serializers.bid import BidSerializer
from openprocurement.tender.competitivedialogue.procedure.state.bid import Stage1BidState
from openprocurement.tender.openeu.procedure.validation import (
    validate_post_bid_status,
    validate_bid_status_update_not_to_pending,
)
from openprocurement.tender.core.procedure.validation import (
    unless_administrator,
    validate_bid_accreditation_level,
    validate_item_owner,
    validate_input_data,
    validate_patch_data,
    validate_data_documents,
    validate_update_deleted_bid,
    validate_bid_operation_period,
    validate_bid_operation_not_in_tendering,
)
from cornice.resource import resource
from logging import getLogger

LOGGER = getLogger(__name__)


@resource(
    name="{}:Tender Bids".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA bids",
)
class CompetitiveDialogueUABidResource(TenderBidResource):

    serializer_class = BidSerializer
    state_class = Stage1BidState

    @json_view(
        content_type="application/json",
        permission="create_bid",
        validators=(
            validate_bid_accreditation_level,
            validate_bid_operation_not_in_tendering,
            validate_bid_operation_period,
            validate_input_data(PostBid),
            validate_post_bid_status,
            validate_data_documents(route_key="bid_id", uid_key="id"),
        ),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        permission="edit_bid",
        validators=(
            validate_bid_operation_not_in_tendering,
            validate_bid_operation_period,

            unless_administrator(validate_item_owner("bid")),
            validate_update_deleted_bid,

            validate_input_data(PatchBid, filters=(filter_administrator_bid_update,), none_means_remove=True),
            validate_patch_data(Bid, item_name="bid"),
            validate_bid_status_update_not_to_pending,
        ),
    )
    def patch(self):
        return super().patch()


@resource(
    name="{}:Tender Bids".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU bids",
)
class CompetitiveDialogueEUBidResource(TenderBidResource):

    serializer_class = BidSerializer
    state_class = Stage1BidState

    @json_view(
        content_type="application/json",
        permission="create_bid",
        validators=(
            validate_bid_accreditation_level,
            validate_bid_operation_not_in_tendering,
            validate_bid_operation_period,
            validate_input_data(PostBid),
            validate_post_bid_status,
            validate_data_documents(route_key="bid_id", uid_key="id"),
        ),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        permission="edit_bid",
        validators=(
            validate_bid_operation_not_in_tendering,
            validate_bid_operation_period,

            unless_administrator(validate_item_owner("bid")),
            validate_update_deleted_bid,

            validate_input_data(PatchBid, filters=(filter_administrator_bid_update,)),
            validate_patch_data(Bid, item_name="bid"),
            validate_bid_status_update_not_to_pending,
        ),
    )
    def patch(self):
        return super().patch()
