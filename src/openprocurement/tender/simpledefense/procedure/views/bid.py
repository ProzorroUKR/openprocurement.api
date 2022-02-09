from openprocurement.tender.openuadefense.procedure.views.bid import TenderBidResource
from openprocurement.tender.core.procedure.validation import (
    validate_bid_operation_period,
    validate_bid_operation_not_in_tendering,
)
from openprocurement.tender.core.procedure.models.bid import filter_administrator_bid_update
from openprocurement.tender.simpledefense.procedure.models.bid import PostBid, PatchBid, Bid
from openprocurement.tender.core.procedure.validation import (
    unless_administrator,
    validate_bid_accreditation_level,
    validate_item_owner,
    validate_input_data,
    validate_patch_data,
    validate_data_documents,
    validate_update_deleted_bid,
)
from openprocurement.api.utils import json_view
from cornice.resource import resource


@resource(
    name="simple.defense:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType="simple.defense",
    description="Tender simple.defense bids",
)
class TenderBidResource(TenderBidResource):
    @json_view(
        content_type="application/json",
        permission="create_bid",
        validators=(
            validate_bid_accreditation_level,
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
        return super().delete()
