from logging import getLogger

from cornice.resource import resource

from openprocurement.api.auth import ACCR_4
from openprocurement.api.procedure.validation import (
    validate_accreditation_level,
    validate_data_documents,
    validate_input_data,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.competitivedialogue.procedure.validation import (
    validate_firm_to_create_bid,
)
from openprocurement.tender.core.procedure.validation import (
    validate_bid_operation_not_in_tendering,
    validate_bid_operation_period,
)
from openprocurement.tender.openeu.procedure.models.bid import PostBid as PostBidEU
from openprocurement.tender.openeu.procedure.views.bid import OpenEUTenderBidResource
from openprocurement.tender.openua.procedure.models.bid import PostBid as PostBidUA
from openprocurement.tender.openua.procedure.views.bid import OpenUATenderBidResource

LOGGER = getLogger(__name__)


@resource(
    name="{}:Tender Bids".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue  Stage2EU bids",
)
class CompetitiveDialogueStage2EUBidResource(OpenEUTenderBidResource):
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
            validate_input_data(PostBidEU),
            validate_firm_to_create_bid,
            validate_data_documents(route_key="bid_id", uid_key="id"),
        ),
    )
    def collection_post(self):
        return super().collection_post()


@resource(
    name="{}:Tender Bids".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue Stage2 UA bids",
)
class CompetitiveDialogueStage2UABidResource(OpenUATenderBidResource):
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
            validate_input_data(PostBidUA),
            validate_firm_to_create_bid,
            validate_data_documents(route_key="bid_id", uid_key="id"),
        ),
    )
    def collection_post(self):
        return super().collection_post()
