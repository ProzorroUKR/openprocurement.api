# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.complaint_post_document import TenderComplaintPostDocumentResource


@optendersresource(
    name="negotiation:Tender Award Complaint Post Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}/documents/{document_id}",
    procurementMethodType="negotiation",
    description="Tender award complaint post documents",
)
class TenderNegotiationAwardComplaintPostDocumentResource(TenderComplaintPostDocumentResource):
    pass


@optendersresource(
    name="negotiation.quick:Tender Award Complaint Post Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}/documents/{document_id}",
    procurementMethodType="negotiation.quick",
    description="Tender award complaint post documents",
)
class TenderNegotiationQuickAwardComplaintPostDocumentResource(TenderComplaintPostDocumentResource):
    pass
