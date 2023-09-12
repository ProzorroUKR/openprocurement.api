from openprocurement.tender.core.procedure.views.award_complaint_document import AwardComplaintDocumentResource
from openprocurement.tender.openua.procedure.state.award_complaint_document import OpenUAAwardComplaintDocumentState
from cornice.resource import resource


@resource(
    name="aboveThresholdUA.defense:Tender Award Complaint Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdUA.defense",
    description="Tender award complaint documents",
)
class OpenUADefenseAwardComplaintDocumentResource(AwardComplaintDocumentResource):
    state_class = OpenUAAwardComplaintDocumentState
