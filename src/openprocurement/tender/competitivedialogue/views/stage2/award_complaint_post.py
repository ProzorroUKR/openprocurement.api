# -*- coding: utf-8 -*-
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.award_complaint_post import (
    TenderAwardComplaintPostResource as BaseTenderAwardComplaintPostResource
)


@optendersresource(
    name="{}:Tender Award Complaint Posts".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender award complaint posts",
)
class TenderCompetitiveDialogueStage2EUAwardComplaintPostResource(BaseTenderAwardComplaintPostResource):
    pass


@optendersresource(
    name="{}:Tender Award Complaint Posts".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Tender award complaint posts",
)
class TenderCompetitiveDialogueStage2UAAwardComplaintPostResource(BaseTenderAwardComplaintPostResource):
    pass
