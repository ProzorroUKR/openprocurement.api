# -*- coding: utf-8 -*-
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.openua.views.complaint_post_document import TenderComplaintPostDocumentResource


@qualifications_resource(
    name="{}:Tender Qualification Complaint Post Documents".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts/{post_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts/{post_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender qualification complaint post documents",
)
class TenderCompetitiveDialogueEUQualificationComplaintPostDocumentResource(TenderComplaintPostDocumentResource):
    pass
