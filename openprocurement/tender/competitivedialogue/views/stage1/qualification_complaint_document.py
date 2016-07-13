# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.openeu.views.qualification_complaint_document import TenderEUAwardComplaintDocumentResource as BaseTenderEUAwardComplaintDocumentResource
from openprocurement.tender.competitivedialogue.models import CD_EU_TYPE, CD_UA_TYPE


@qualifications_resource(
    name='Competitive Dialogue EU Qualification Complaint Documents',
    collection_path='/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/documents',
    path='/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/documents/{document_id}',
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU Qualification Complaint Documents")
class CompetitiveDialogueEUQualificationComplaintDocumentResource(BaseTenderEUAwardComplaintDocumentResource):
    pass


@qualifications_resource(
    name='Competitive Dialogue UA Qualification Complaint Documents',
    collection_path='/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/documents',
    path='/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/documents/{document_id}',
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA Qualification Complaint Documents")
class CompetitiveDialogueUAQualificationComplaintDocumentResource(BaseTenderEUAwardComplaintDocumentResource):
    pass
