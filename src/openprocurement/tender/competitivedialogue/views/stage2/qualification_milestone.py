# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.qualification_milestone import BaseQualificationMilestoneResource
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE


@qualifications_resource(
    name="{}:Tender Qualification Milestones".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/milestones/{milestone_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender qualification milestones",
)
class TenderEUQualificationMilestoneResource(BaseQualificationMilestoneResource):
    pass
