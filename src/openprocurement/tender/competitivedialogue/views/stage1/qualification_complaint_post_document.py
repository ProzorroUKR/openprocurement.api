# -*- coding: utf-8 -*-
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.openua.views.complaint_post_document import TenderComplaintPostDocumentResource


@qualifications_resource(
    name="{}:Tender Qualification Complaint Post Documents".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts/{post_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts/{post_id}/documents/{document_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Tender qualification complaint post documents",
)
class TenderCompetitiveDialogueEUQualificationComplaintPostDocumentResource(TenderComplaintPostDocumentResource):
    pass


@qualifications_resource(
    name="{}:Tender Qualification Complaint Post Documents".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts/{post_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts/{post_id}/documents/{document_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Tender qualification complaint post documents",
)
class TenderCompetitiveDialogueUAQualificationComplaintPostDocumentResource(TenderComplaintPostDocumentResource):
    pass
