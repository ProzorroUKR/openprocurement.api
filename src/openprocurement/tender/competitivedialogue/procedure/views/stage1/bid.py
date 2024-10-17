from logging import getLogger

from cornice.resource import resource

from openprocurement.api.auth import ACCR_4
from openprocurement.api.procedure.validation import (
    unless_administrator,
    validate_accreditation_level,
    validate_data_documents,
    validate_input_data,
    validate_item_owner,
    validate_patch_data_simple,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.competitivedialogue.procedure.models.bid import (
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
    validate_update_deleted_bid,
)
from openprocurement.tender.openeu.procedure.views.bid import OpenEUTenderBidResource

LOGGER = getLogger(__name__)


@resource(
    name="{}:Tender Bids".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA bids",
)
class CompetitiveDialogueUABidResource(OpenEUTenderBidResource):
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
            validate_bid_operation_not_in_tendering,
            validate_bid_operation_period,
            unless_administrator(validate_item_owner("bid")),
            validate_update_deleted_bid,
            validate_input_data(PatchBid, filters=(filter_administrator_bid_update,), none_means_remove=True),
            validate_patch_data_simple(Bid, item_name="bid"),
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
class CompetitiveDialogueEUBidResource(OpenEUTenderBidResource):
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
            validate_bid_operation_not_in_tendering,
            validate_bid_operation_period,
            unless_administrator(validate_item_owner("bid")),
            validate_update_deleted_bid,
            validate_input_data(PatchBid, filters=(filter_administrator_bid_update,)),
            validate_patch_data_simple(Bid, item_name="bid"),
        ),
    )
    def patch(self):
        return super().patch()
