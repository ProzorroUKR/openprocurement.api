# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.openeu.views.qualification_document import TenderQualificationDocumentResource as BaseTenderQualificationDocumentResource


@qualifications_resource(
    name='Competitive Dialogue EU Qualification Documents',
    collection_path='/tenders/{tender_id}/qualifications/{qualification_id}/documents',
    path='/tenders/{tender_id}/qualifications/{qualification_id}/documents/{document_id}',
    procurementMethodType='competitiveDialogue.aboveThresholdEU',
    description="Competitive Dialogue EU Qualification Documents")
class CompetitiveDialogueEUQualificationDocumentResource(BaseTenderQualificationDocumentResource):
    pass


@qualifications_resource(
    name='Competitive Dialogue UA Qualification Documents',
    collection_path='/tenders/{tender_id}/qualifications/{qualification_id}/documents',
    path='/tenders/{tender_id}/qualifications/{qualification_id}/documents/{document_id}',
    procurementMethodType='competitiveDialogue.aboveThresholdUA',
    description="Competitive Dialogue UA Qualification Documents")
class CompetitiveDialogueUAQualificationDocumentResource(BaseTenderQualificationDocumentResource):
    pass
