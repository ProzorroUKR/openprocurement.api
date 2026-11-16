from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.question import TenderQuestionResource
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX, OpenProcurementMethodType
from openprocurement.tender.open.procedure.state.question import (
    AboveThresholdEUTenderQuestionState,
    AboveThresholdTenderQuestionState,
    AboveThresholdUATenderQuestionState,
    BelowThresholdTenderQuestionState,
    COTenderQuestionState,
    DefenseTenderQuestionState,
    OpenTenderingTenderQuestionState,
    RFPTenderQuestionState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Questions",
    collection_path="/tenders/{tender_id}/questions",
    path="/tenders/{tender_id}/questions/{question_id}",
    description="Tender questions",
    procurementMethodType=OpenProcurementMethodType,
)
class OpenTenderQuestionResource(TenderQuestionResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: AboveThresholdTenderQuestionState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: AboveThresholdUATenderQuestionState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdEUTenderQuestionState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingTenderQuestionState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE: DefenseTenderQuestionState,
        ProcurementMethodType.SIMPLE_DEFENSE: AboveThresholdUATenderQuestionState,
        ProcurementMethodType.COMPETITIVE_ORDERING: COTenderQuestionState,
        ProcurementMethodType.BELOW_THRESHOLD: BelowThresholdTenderQuestionState,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL: RFPTenderQuestionState,
    }
