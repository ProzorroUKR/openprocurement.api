from openprocurement.tender.openeu.procedure.views.bid import TenderBidResource as BaseResourceEU
from openprocurement.tender.openua.procedure.views.bid import TenderBidResource as BaseResourceUA
from openprocurement.tender.competitivedialogue.constants import STAGE_2_UA_TYPE, STAGE_2_EU_TYPE
from openprocurement.tender.competitivedialogue.procedure.validation import validate_firm_to_create_bid
from openprocurement.tender.openeu.procedure.models.bid import PostBid as PostBidEU
from openprocurement.tender.openua.procedure.models.bid import PostBid as PostBidUA
from openprocurement.tender.openeu.procedure.validation import (
    validate_post_bid_status,
)
from openprocurement.tender.core.procedure.validation import (
    validate_bid_accreditation_level,
    validate_input_data,
    validate_data_documents,
    validate_bid_operation_period,
    validate_bid_operation_not_in_tendering,
)
from openprocurement.api.utils import json_view
from cornice.resource import resource
from logging import getLogger

LOGGER = getLogger(__name__)


@resource(
    name="{}:Tender Bids".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue  Stage2EU bids",
)
class CompetitiveDialogueStage2EUBidResource(BaseResourceEU):
    @json_view(
        content_type="application/json",
        permission="create_bid",
        validators=(
            validate_bid_accreditation_level,
            validate_bid_operation_not_in_tendering,
            validate_bid_operation_period,
            validate_input_data(PostBidEU),
            validate_post_bid_status,
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
class CompetitiveDialogueStage2UABidResource(BaseResourceUA):
    @json_view(
        content_type="application/json",
        permission="create_bid",
        validators=(
            validate_bid_accreditation_level,
            validate_bid_operation_not_in_tendering,
            validate_bid_operation_period,
            validate_input_data(PostBidUA),
            validate_firm_to_create_bid,
            validate_data_documents(route_key="bid_id", uid_key="id"),
        ),
    )
    def collection_post(self):
        return super().collection_post()
