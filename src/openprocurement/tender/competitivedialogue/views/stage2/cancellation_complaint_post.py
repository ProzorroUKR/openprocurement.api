# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.cancellation_complaint_post import (
    TenderCancellationComplaintPostResource as BaseTenderCancellationComplaintPostResource,
)
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE


@optendersresource(
    name="{}:Tender Cancellation Complaint Posts".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender cancellation complaint posts",
)
class CompetitiveDialogueStage2EUCancellationComplaintPostResource(
    BaseTenderCancellationComplaintPostResource
):
    pass


@optendersresource(
    name="{}:Tender Cancellation Complaint Posts".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Tender cancellation complaint posts",
)
class CompetitiveDialogueStage2UACancellationComplaintPostResource(
    BaseTenderCancellationComplaintPostResource
):
    pass
