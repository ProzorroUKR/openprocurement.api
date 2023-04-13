from openprocurement.api.utils import json_view, raise_operation_error
from openprocurement.tender.core.procedure.validation import (
    validate_bid_operation_period,
    validate_bid_operation_not_in_tendering,
    unless_administrator,
    validate_bid_accreditation_level,
    validate_item_owner,
    validate_input_data,
    validate_patch_data,
    validate_data_documents,
)
from openprocurement.tender.belowthreshold.procedure.views.bid import TenderBidResource
from openprocurement.tender.core.procedure.models.bid import filter_administrator_bid_update
from openprocurement.tender.pricequotation.procedure.models.bid import PostBid, PatchBid, Bid
from openprocurement.tender.pricequotation.constants import PQ
from cornice.resource import resource
from logging import getLogger

LOGGER = getLogger(__name__)


@resource(
    name="{}:Tender Bids".format(PQ),
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType=PQ,
    description="Tender bids",
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
            validate_bid_operation_not_in_tendering,
            validate_bid_operation_period,  # validations before forbidding, hmm...
        )
    )
    def delete(self):
        """
        Cancelling the proposal.
        Forbidden for price quotation tender.
        """
        request = self.request
        raise_operation_error(
            request,
            "Can't delete bid in Price Quotation tender",
        )
