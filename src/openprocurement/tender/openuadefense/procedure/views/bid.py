from logging import getLogger

from cornice.resource import resource

from openprocurement.api.auth import AccreditationLevel
from openprocurement.api.procedure.validation import (
    unless_administrator,
    validate_accreditation_level,
    validate_data_documents,
    validate_input_data,
    validate_input_data_from_resolved_model,
    validate_item_owner,
    validate_patch_data_simple,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.models.bid import (
    filter_administrator_bid_update,
)
from openprocurement.tender.core.procedure.validation import (
    unless_allowed_by_qualification_milestone_24,
    validate_bid_operation_not_in_tendering,
    validate_bid_operation_period,
    validate_update_deleted_bid,
)
from openprocurement.tender.openua.procedure.views.bid import OpenUATenderBidResource
from openprocurement.tender.openuadefense.procedure.models.bid import Bid, PostBid
from openprocurement.tender.openuadefense.procedure.state.bid import (
    OpenUADefenseBidState,
)

LOGGER = getLogger(__name__)


@resource(
    name="aboveThresholdUA.defense:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType="aboveThresholdUA.defense",
    description="Tender UA.defense bids",
)
class OpenUADefenseTenderBidResource(OpenUATenderBidResource):
    model_class = Bid
    state_class = OpenUADefenseBidState

    @json_view(
        content_type="application/json",
        permission="create_bid",
        validators=(
            validate_accreditation_level(
                levels=(AccreditationLevel.ACCR_4,),
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
            unless_allowed_by_qualification_milestone_24(
                validate_bid_operation_not_in_tendering,
                validate_bid_operation_period,
            ),
            validate_input_data_from_resolved_model(
                filters=(filter_administrator_bid_update,),
                none_means_remove=True,
            ),
            validate_patch_data_simple(Bid, item_name="bid"),
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
