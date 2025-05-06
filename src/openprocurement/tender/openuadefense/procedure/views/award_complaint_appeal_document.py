from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_complaint_appeal_document import (
    BaseAwardComplaintAppealDocumentResource,
)
from openprocurement.tender.openuadefense.constants import ABOVE_THRESHOLD_UA_DEFENSE


@resource(
    name=f"{ABOVE_THRESHOLD_UA_DEFENSE}:Tender Award Complaint Appeal Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType=ABOVE_THRESHOLD_UA_DEFENSE,
    description="Tender award complaint appeal documents",
)
class OpenUADefenseAwardComplaintAppealDocumentResource(BaseAwardComplaintAppealDocumentResource):
    pass
