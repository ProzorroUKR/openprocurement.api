# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.openeu.views.qualification_complaint import TenderEUQualificationComplaintResource as BaseTenderQualificationComplaintResource


@qualifications_resource(
    name='Competitive Dialogue EU Qualification Complaints',
    collection_path='/tenders/{tender_id}/qualifications/{qualification_id}/complaints',
    path='/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}',
    procurementMethodType='competitiveDialogue.aboveThresholdEU',
    description="Competitive Dialogue EU qualification complaints")
class CompetitiveDialogueEUQualificationComplaintResource(BaseTenderQualificationComplaintResource):
    pass


@qualifications_resource(
    name='Competitive Dialogue UA Qualification Complaints',
    collection_path='/tenders/{tender_id}/qualifications/{qualification_id}/complaints',
    path='/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}',
    procurementMethodType='competitiveDialogue.aboveThresholdUA',
    description="Competitive Dialogue UA qualification complaints")
class CompetitiveDialogueUAQualificationComplaintResource(BaseTenderQualificationComplaintResource):
    pass
