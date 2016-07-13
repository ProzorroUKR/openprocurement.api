# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.openeu.views.qualification import TenderQualificationResource
from openprocurement.tender.competitivedialogue.models import CD_EU_TYPE, CD_UA_TYPE

@qualifications_resource(
    name='Competitive Dialogue EU Qualification',
    collection_path='/tenders/{tender_id}/qualifications',
    path='/tenders/{tender_id}/qualifications/{qualification_id}',
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU Qualification")
class CompetitiveDialogueEUQualificationResource(TenderQualificationResource):
    pass


@qualifications_resource(
    name='Competitive Dialogue UA Qualification',
    collection_path='/tenders/{tender_id}/qualifications',
    path='/tenders/{tender_id}/qualifications/{qualification_id}',
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA Qualification")
class CompetitiveDialogueUAQualificationResource(TenderQualificationResource):
    pass
