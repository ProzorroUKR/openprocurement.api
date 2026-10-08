from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_req_response import AwardReqResponseResource
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD,
    ABOVE_THRESHOLD_EU,
    ABOVE_THRESHOLD_UA,
    BELOW_THRESHOLD,
    COMPETITIVE_ORDERING,
    OPEN_ROUTE_PREFIX,
    REQUEST_FOR_PROPOSAL,
)
from openprocurement.tender.open.procedure.state.award_req_response import (
    AboveThresholdAwardReqResponseState,
    AboveThresholdUAAwardReqResponseState,
    BelowThresholdAwardReqResponseState,
    COAwardReqResponseState,
    RFPAwardReqResponseState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Award Requirement Response",
    collection_path="/tenders/{tender_id}/awards/{award_id}/requirement_responses",
    path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}",
    description="Tender award requirement responses",
    procurementMethodType=[
        ABOVE_THRESHOLD,
        ABOVE_THRESHOLD_UA,
        ABOVE_THRESHOLD_EU,
        COMPETITIVE_ORDERING,
        BELOW_THRESHOLD,
        REQUEST_FOR_PROPOSAL,
    ],
)
class OpenAwardReqResponseResource(AwardReqResponseResource):
    state_classes = {
        ABOVE_THRESHOLD: AboveThresholdAwardReqResponseState,
        ABOVE_THRESHOLD_UA: AboveThresholdUAAwardReqResponseState,
        ABOVE_THRESHOLD_EU: AboveThresholdUAAwardReqResponseState,
        COMPETITIVE_ORDERING: COAwardReqResponseState,
        BELOW_THRESHOLD: BelowThresholdAwardReqResponseState,
        REQUEST_FOR_PROPOSAL: RFPAwardReqResponseState,
    }
