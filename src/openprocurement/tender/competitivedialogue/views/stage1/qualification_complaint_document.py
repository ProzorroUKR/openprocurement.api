# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.openeu.views.qualification_complaint_document import (
    TenderEUQualificationComplaintDocumentResource as BaseTenderEUQualificationComplaintDocumentResource
)
from openprocurement.tender.competitivedialogue.constants import (
    CD_EU_TYPE, CD_UA_TYPE
)


@qualifications_resource(
    name='{}:Tender Qualification Complaint Documents'.format(CD_EU_TYPE),
    collection_path='/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/documents',
    path='/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/documents/{document_id}',
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU Qualification Complaint Documents")
class CompetitiveDialogueEUQualificationComplaintDocumentResource(BaseTenderEUQualificationComplaintDocumentResource):
    pass


@qualifications_resource(
    name='{}:Tender Qualification Complaint Documents'.format(CD_UA_TYPE),
    collection_path='/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/documents',
    path='/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/documents/{document_id}',
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA Qualification Complaint Documents")
class CompetitiveDialogueUAQualificationComplaintDocumentResource(BaseTenderEUQualificationComplaintDocumentResource):
    pass
