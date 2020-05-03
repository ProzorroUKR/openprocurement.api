# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.qualification_milestone import BaseQualificationMilestoneResource
from openprocurement.tender.openeu.utils import qualifications_resource


@qualifications_resource(
    name="aboveThresholdEU:Tender Qualification Milestones",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones/{milestone_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender EU qualification milestones",
)
class TenderQualificationMilestoneResource(BaseQualificationMilestoneResource):
    pass
