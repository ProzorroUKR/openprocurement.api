# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.openeu.views.qualification_document import TenderQualificationDocumentResource
from openprocurement.tender.competitivedialogue.models import STAGE_2_EU_TYPE


@qualifications_resource(
    name='Competitive Dialogue Stage 2 EU Qualification Documents',
    collection_path='/tenders/{tender_id}/qualifications/{qualification_id}/documents',
    path='/tenders/{tender_id}/qualifications/{qualification_id}/documents/{document_id}',
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage 2 EU qualification documents")
class CompetitiveDialogueStage2QualificationDocumentResource(TenderQualificationDocumentResource):
    pass
