from cornice.resource import resource

from openprocurement.tender.belowthreshold.procedure.state.award_complaint_document import (
    BTAwardComplaintDocumentState,
)
from openprocurement.tender.core.procedure.views.award_complaint_document import (
    AwardComplaintDocumentResource,
)


@resource(
    name="belowThreshold:Tender Award Complaint Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType="belowThreshold",
    description="Tender award complaint documents",
)
class BelowThresholdAwardComplaintDocumentResource(AwardComplaintDocumentResource):
    state_class = BTAwardComplaintDocumentState
