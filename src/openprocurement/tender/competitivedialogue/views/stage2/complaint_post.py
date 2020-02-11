# -*- coding: utf-8 -*-
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from openprocurement.tender.core.utils import optendersresource

from openprocurement.tender.openua.views.complaint_post import (
    TenderComplaintPostResource as BaseTenderComplaintPostResource
)


@optendersresource(
    name="{}:Tender Complaint Posts".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender complaint posts",
)
class CompetitiveDialogueStage2EUTenderComplaintPostResource(BaseTenderComplaintPostResource):
    pass


@optendersresource(
    name="{}:Tender Complaint Posts".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Tender complaint posts",
)
class CompetitiveDialogueStage2UATenderComplaintPostResource(BaseTenderComplaintPostResource):
    pass
