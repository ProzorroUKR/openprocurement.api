from openprocurement.tender.core.procedure.views.award_complaint_document import AwardComplaintDocumentResource
from openprocurement.tender.openua.procedure.state.award_complaint_document import OpenUAAwardComplaintDocumentState
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from cornice.resource import resource


@resource(
    name="{}:Tender Award Complaint Documents".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage 2 award complaint documents",
)
class CD2EUAwardComplaintDocumentResource(AwardComplaintDocumentResource):
    state_class = OpenUAAwardComplaintDocumentState


@resource(
    name="{}:Tender Award Complaint Documents".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue Stage 2 award complaint documents",
)
class CD2UAAwardComplaintDocumentResource(AwardComplaintDocumentResource):
    state_class = OpenUAAwardComplaintDocumentState
