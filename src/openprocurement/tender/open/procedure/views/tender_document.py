from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.tender_document import TenderDocumentResource
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX, OpenProcurementMethodType
from openprocurement.tender.open.procedure.state.tender_document import (
    AboveThresholdTenderDocumentState,
    AboveThresholdUATenderDocumentState,
    BelowThresholdTenderDocumentState,
    COTenderDocumentState,
    OpenTenderingTenderDocumentState,
    RFPTenderDocumentState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    description="Tender related binary files (PDFs, etc.)",
    procurementMethodType=OpenProcurementMethodType,
)
class OpenTenderDocumentResource(TenderDocumentResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: AboveThresholdTenderDocumentState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: AboveThresholdUATenderDocumentState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdUATenderDocumentState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingTenderDocumentState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE: AboveThresholdUATenderDocumentState,
        ProcurementMethodType.SIMPLE_DEFENSE: AboveThresholdUATenderDocumentState,
        ProcurementMethodType.COMPETITIVE_ORDERING: COTenderDocumentState,
        ProcurementMethodType.BELOW_THRESHOLD: BelowThresholdTenderDocumentState,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL: RFPTenderDocumentState,
    }
