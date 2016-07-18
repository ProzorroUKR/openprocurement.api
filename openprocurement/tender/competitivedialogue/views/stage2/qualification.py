# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.openeu.views.qualification import TenderQualificationResource
from openprocurement.tender.competitivedialogue.models import STAGE_2_EU_TYPE


@qualifications_resource(
    name='Competitive Dialogue Stage 2 EU Qualification',
    collection_path='/tenders/{tender_id}/qualifications',
    path='/tenders/{tender_id}/qualifications/{qualification_id}',
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage 2 EU Qualification")
class CompetitiveDialogueStage2(TenderQualificationResource):
    pass
