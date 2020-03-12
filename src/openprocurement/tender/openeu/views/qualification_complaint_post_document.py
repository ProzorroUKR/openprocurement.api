# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.openua.views.complaint_post_document import TenderComplaintPostDocumentResource


@qualifications_resource(
    name="aboveThresholdEU:Tender Qualification Complaint Post Documents",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts/{post_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts/{post_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender qualification complaint post documents",
)
class TenderQualificationComplaintPostDocumentResource(TenderComplaintPostDocumentResource):
    pass
