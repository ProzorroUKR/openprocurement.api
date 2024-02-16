from logging import getLogger

from cornice.resource import resource

from openprocurement.api.auth import ACCR_2
from openprocurement.api.procedure.validation import (
    unless_administrator,
    validate_accreditation_level,
    validate_data_documents,
    validate_input_data,
    validate_item_owner,
    validate_patch_data,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.belowthreshold.procedure.models.bid import (
    Bid,
    PatchBid,
    PostBid,
)
from openprocurement.tender.core.procedure.models.bid import (
    filter_administrator_bid_update,
)
from openprocurement.tender.core.procedure.validation import (
    validate_bid_operation_not_in_tendering,
    validate_bid_operation_period,
)
from openprocurement.tender.core.procedure.views.bid import TenderBidResource

LOGGER = getLogger(__name__)


@resource(
    name="belowThreshold:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType="belowThreshold",
    description="Tender bids",
)
class TenderBidResource(TenderBidResource):
    @json_view(
        content_type="application/json",
        permission="create_bid",
        validators=(
            validate_accreditation_level(
                levels=(ACCR_2,),
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
        ),
    )
    def delete(self):
        return super().delete()
