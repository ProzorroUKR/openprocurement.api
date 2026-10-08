from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_complaint_document import AwardComplaintDocumentResource
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
from openprocurement.tender.open.procedure.state.award_complaint_document import (
    AboveThresholdAwardComplaintDocumentState,
    AboveThresholdUAAwardComplaintDocumentState,
    BelowThresholdAwardComplaintDocumentState,
    COAwardComplaintDocumentState,
    RFPAwardComplaintDocumentState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Award Complaint Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}",
    description="Tender award complaint documents",
    procurementMethodType=OPEN_PROCUREMENT_METHOD_TYPES,
)
class OpenAwardComplaintDocumentResource(AwardComplaintDocumentResource):
    state_classes = {
        ABOVE_THRESHOLD: AboveThresholdAwardComplaintDocumentState,
        ABOVE_THRESHOLD_UA: AboveThresholdUAAwardComplaintDocumentState,
        ABOVE_THRESHOLD_EU: AboveThresholdUAAwardComplaintDocumentState,
        ABOVE_THRESHOLD_UA_DEFENSE: AboveThresholdUAAwardComplaintDocumentState,
        SIMPLE_DEFENSE: AboveThresholdUAAwardComplaintDocumentState,
        COMPETITIVE_ORDERING: COAwardComplaintDocumentState,
        BELOW_THRESHOLD: BelowThresholdAwardComplaintDocumentState,
        REQUEST_FOR_PROPOSAL: RFPAwardComplaintDocumentState,
    }
