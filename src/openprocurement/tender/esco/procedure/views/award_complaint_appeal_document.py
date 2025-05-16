from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_complaint_appeal_document import (
    BaseAwardComplaintAppealDocumentResource,
)
from openprocurement.tender.esco.constants import ESCO


@resource(
    name=f"{ESCO}:Tender Award Complaint Appeal Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType=ESCO,
    description="Tender award complaint appeal documents",
)
class ESCOAwardComplaintAppealDocumentResource(BaseAwardComplaintAppealDocumentResource):
    pass
