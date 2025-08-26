from logging import getLogger

from cornice.resource import resource

from openprocurement.api.auth import AccreditationLevel
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
from openprocurement.tender.cfaselectionua.procedure.models.bid import (
    Bid,
    PatchBid,
    PostBid,
)
from openprocurement.tender.cfaselectionua.procedure.serializers.bid import (
    BidSerializer,
)
from openprocurement.tender.cfaselectionua.procedure.state.bid import BidState
from openprocurement.tender.core.procedure.mask import TENDER_MASK_MAPPING
from openprocurement.tender.core.procedure.models.bid import (
    filter_administrator_bid_update,
)
from openprocurement.tender.core.procedure.serializers.tender import (
    TenderBaseSerializer,
)
from openprocurement.tender.core.procedure.validation import (
    unless_allowed_by_qualification_milestone_24,
    validate_bid_operation_in_tendering,
    validate_bid_operation_not_in_tendering,
    validate_bid_operation_period,
    validate_update_deleted_bid,
)
from openprocurement.tender.core.procedure.views.bid import TenderBidResource
from openprocurement.tender.core.utils import context_view

LOGGER = getLogger(__name__)


@resource(
    name="closeFrameworkAgreementSelectionUA:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender bids",
)
class CFASelectionTenderBidResource(TenderBidResource):
    serializer_class = BidSerializer
    state_class = BidState

    @json_view(
        permission="view_tender",
        validators=(validate_bid_operation_in_tendering,),
    )
    def collection_get(self):
        return super().collection_get()

    @json_view(
        permission="view_tender",
        validators=(
            unless_item_owner(
                validate_bid_operation_in_tendering,
                item_name="bid",
            ),
        ),
    )
    @context_view(
        objs={
            "tender": (TenderBaseSerializer, TENDER_MASK_MAPPING),
        }
    )
    def get(self):
        return super().get()

    @json_view(
        content_type="application/json",
        permission="create_bid",
        validators=(
            validate_accreditation_level(
                levels=(AccreditationLevel.ACCR_2,),
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
            unless_allowed_by_qualification_milestone_24(
                validate_bid_operation_not_in_tendering,
                validate_bid_operation_period,
            ),
        ),
    )
    def patch(self):
        return super().patch()

    @json_view(
        content_type="application/json",
        permission="edit_bid",
        validators=(
            validate_bid_operation_not_in_tendering,
            validate_bid_operation_period,
        ),
    )
    def delete(self):
        return super().delete()
