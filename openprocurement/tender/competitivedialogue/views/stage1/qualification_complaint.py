# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.openeu.views.qualification_complaint import (
    TenderEUQualificationComplaintResource as BaseTenderQualificationComplaintResource
)
from openprocurement.tender.competitivedialogue.constants import (
    CD_EU_TYPE, CD_UA_TYPE
)

@qualifications_resource(
    name='{}:Tender Qualification Complaints'.format(CD_EU_TYPE),
    collection_path='/tenders/{tender_id}/qualifications/{qualification_id}/complaints',
    path='/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}',
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU qualification complaints")
class CompetitiveDialogueEUQualificationComplaintResource(BaseTenderQualificationComplaintResource):
    pass


@qualifications_resource(
    name='{}:Tender Qualification Complaints'.format(CD_UA_TYPE),
    collection_path='/tenders/{tender_id}/qualifications/{qualification_id}/complaints',
    path='/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}',
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA qualification complaints")
class CompetitiveDialogueUAQualificationComplaintResource(BaseTenderQualificationComplaintResource):
    pass
