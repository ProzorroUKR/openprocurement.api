from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.award_req_response import AwardReqResponseResource
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX
from openprocurement.tender.open.procedure.state.award_req_response import (
    AboveThresholdAwardReqResponseState,
    AboveThresholdUAAwardReqResponseState,
    BelowThresholdAwardReqResponseState,
    COAwardReqResponseState,
    OpenTenderingAwardReqResponseState,
    RFPAwardReqResponseState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Award Requirement Response",
    collection_path="/tenders/{tender_id}/awards/{award_id}/requirement_responses",
    path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}",
    description="Tender award requirement responses",
    procurementMethodType=[
        ProcurementMethodType.ABOVE_THRESHOLD,
        ProcurementMethodType.ABOVE_THRESHOLD_UA,
        ProcurementMethodType.ABOVE_THRESHOLD_EU,
        ProcurementMethodType.OPEN_TENDERING,
        ProcurementMethodType.COMPETITIVE_ORDERING,
        ProcurementMethodType.BELOW_THRESHOLD,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL,
    ],
)
class OpenAwardReqResponseResource(AwardReqResponseResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: AboveThresholdAwardReqResponseState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: AboveThresholdUAAwardReqResponseState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdUAAwardReqResponseState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingAwardReqResponseState,
        ProcurementMethodType.COMPETITIVE_ORDERING: COAwardReqResponseState,
        ProcurementMethodType.BELOW_THRESHOLD: BelowThresholdAwardReqResponseState,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL: RFPAwardReqResponseState,
    }
