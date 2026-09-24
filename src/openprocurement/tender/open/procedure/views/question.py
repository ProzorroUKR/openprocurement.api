from cornice.resource import resource

from openprocurement.tender.core.procedure.views.question import TenderQuestionResource
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD,
    ABOVE_THRESHOLD_EU,
    ABOVE_THRESHOLD_UA,
    ABOVE_THRESHOLD_UA_DEFENSE,
    BELOW_THRESHOLD,
    COMPETITIVE_ORDERING,
    OPEN_PROCUREMENT_METHOD_TYPES,
    OPEN_ROUTE_PREFIX,
    REQUEST_FOR_PROPOSAL,
    SIMPLE_DEFENSE,
)
from openprocurement.tender.open.procedure.state.question import (
    AboveThresholdEUTenderQuestionState,
    AboveThresholdTenderQuestionState,
    AboveThresholdUATenderQuestionState,
    BelowThresholdTenderQuestionState,
    COTenderQuestionState,
    DefenseTenderQuestionState,
    RFPTenderQuestionState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Questions",
    collection_path="/tenders/{tender_id}/questions",
    path="/tenders/{tender_id}/questions/{question_id}",
    description="Tender questions",
    procurementMethodType=OPEN_PROCUREMENT_METHOD_TYPES,
)
class OpenTenderQuestionResource(TenderQuestionResource):
    state_classes = {
        ABOVE_THRESHOLD: AboveThresholdTenderQuestionState,
        ABOVE_THRESHOLD_UA: AboveThresholdUATenderQuestionState,
        ABOVE_THRESHOLD_EU: AboveThresholdEUTenderQuestionState,
        ABOVE_THRESHOLD_UA_DEFENSE: DefenseTenderQuestionState,
        SIMPLE_DEFENSE: AboveThresholdUATenderQuestionState,
        COMPETITIVE_ORDERING: COTenderQuestionState,
        BELOW_THRESHOLD: BelowThresholdTenderQuestionState,
        REQUEST_FOR_PROPOSAL: RFPTenderQuestionState,
    }
