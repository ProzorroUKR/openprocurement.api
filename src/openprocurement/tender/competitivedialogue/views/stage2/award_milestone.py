# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.award_milestone import BaseAwardMilestoneResource
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.competitivedialogue.constants import STAGE_2_UA_TYPE


@optendersresource(
    name="{}:Tender Award Milestones".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/milestones",
    path="/tenders/{tender_id}/awards/{award_id}/milestones/{milestone_id}",
    description="Tender award milestones",
    procurementMethodType=STAGE_2_UA_TYPE,
)
class TenderUaAwardResource(BaseAwardMilestoneResource):
    pass
