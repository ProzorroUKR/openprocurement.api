# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.openeu.views.qualification import TenderQualificationResource


@qualifications_resource(
    name='Competitive Dialogue EU Qualification',
    collection_path='/tenders/{tender_id}/qualifications',
    path='/tenders/{tender_id}/qualifications/{qualification_id}',
    procurementMethodType='competitiveDialogue.aboveThresholdEU',
    description="Competitive Dialogue EU Qualification")
class CompetitiveDialogueEUQualificationResource(TenderQualificationResource):
    pass


@qualifications_resource(
    name='Competitive Dialogue UA Qualification',
    collection_path='/tenders/{tender_id}/qualifications',
    path='/tenders/{tender_id}/qualifications/{qualification_id}',
    procurementMethodType='competitiveDialogue.aboveThresholdUA',
    description="Competitive Dialogue UA Qualification")
class CompetitiveDialogueUAQualificationResource(TenderQualificationResource):
    pass
