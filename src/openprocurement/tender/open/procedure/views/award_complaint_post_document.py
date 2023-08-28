from openprocurement.tender.core.procedure.views.award_complaint_post_document import (
    BaseAwardComplaintPostDocumentResource,
)
from openprocurement.tender.open.constants import ABOVE_THRESHOLD_GROUP_NAME, ABOVE_THRESHOLD_GROUP
from cornice.resource import resource


@resource(
    name=f"{ABOVE_THRESHOLD_GROUP_NAME}:Tender Award Complaint Post Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}/documents/{document_id}",
    procurementMethodType=ABOVE_THRESHOLD_GROUP,
    description="Tender award complaint post documents",
)
class OpenAwardComplaintPostDocumentResource(BaseAwardComplaintPostDocumentResource):
    pass
