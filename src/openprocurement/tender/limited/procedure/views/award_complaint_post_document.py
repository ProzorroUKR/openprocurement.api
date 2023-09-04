from openprocurement.tender.core.procedure.views.award_complaint_post_document import (
    BaseAwardComplaintPostDocumentResource,
)
from cornice.resource import resource


@resource(
    name="negotiation:Tender Award Complaint Post Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}/documents/{document_id}",
    procurementMethodType="negotiation",
    description="Tender award complaint post documents",
)
class NegotiationAwardComplaintPostDocumentResource(BaseAwardComplaintPostDocumentResource):
    pass


@resource(
    name="negotiation.quick:Tender Award Complaint Post Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}/documents/{document_id}",
    procurementMethodType="negotiation.quick",
    description="Tender award complaint post documents",
)
class NegotiationQuickAwardComplaintPostDocumentResource(BaseAwardComplaintPostDocumentResource):
    pass
