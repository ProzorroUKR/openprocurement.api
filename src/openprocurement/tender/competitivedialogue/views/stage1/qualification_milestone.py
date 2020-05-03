# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.qualification_milestone import BaseQualificationMilestoneResource
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE


@qualifications_resource(
    name="{}:Tender Qualification Milestones".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones/{milestone_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Tender qualification milestones",
)
class TenderUAQualificationMilestoneResource(BaseQualificationMilestoneResource):
    pass


@qualifications_resource(
    name="{}:Tender Qualification Milestones".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones/{milestone_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Tender qualification milestones",
)
class TenderEUQualificationMilestoneResource(BaseQualificationMilestoneResource):
    pass
