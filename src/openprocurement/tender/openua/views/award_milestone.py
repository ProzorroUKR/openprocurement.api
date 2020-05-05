# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.award_milestone import BaseAwardMilestoneResource
from openprocurement.tender.core.utils import optendersresource


@optendersresource(
    name="aboveThresholdUA:Tender Award Milestones",
    collection_path="/tenders/{tender_id}/awards/{award_id}/milestones",
    path="/tenders/{tender_id}/awards/{award_id}/milestones/{milestone_id}",
    description="Tender award milestones",
    procurementMethodType="aboveThresholdUA",
)
class TenderUaAwardResource(BaseAwardMilestoneResource):
    pass
