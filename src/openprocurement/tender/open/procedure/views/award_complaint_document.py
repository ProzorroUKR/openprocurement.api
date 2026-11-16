from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.award_complaint_document import AwardComplaintDocumentResource
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX, OpenProcurementMethodType
from openprocurement.tender.open.procedure.state.award_complaint_document import (
    AboveThresholdAwardComplaintDocumentState,
    AboveThresholdUAAwardComplaintDocumentState,
    BelowThresholdAwardComplaintDocumentState,
    COAwardComplaintDocumentState,
    OpenTenderingAwardComplaintDocumentState,
    RFPAwardComplaintDocumentState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Award Complaint Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}",
    description="Tender award complaint documents",
    procurementMethodType=OpenProcurementMethodType,
)
class OpenAwardComplaintDocumentResource(AwardComplaintDocumentResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: AboveThresholdAwardComplaintDocumentState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: AboveThresholdUAAwardComplaintDocumentState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdUAAwardComplaintDocumentState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingAwardComplaintDocumentState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE: AboveThresholdUAAwardComplaintDocumentState,
        ProcurementMethodType.SIMPLE_DEFENSE: AboveThresholdUAAwardComplaintDocumentState,
        ProcurementMethodType.COMPETITIVE_ORDERING: COAwardComplaintDocumentState,
        ProcurementMethodType.BELOW_THRESHOLD: BelowThresholdAwardComplaintDocumentState,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL: RFPAwardComplaintDocumentState,
    }
