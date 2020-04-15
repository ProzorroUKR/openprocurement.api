# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.cancellation_complaint_post import (
    TenderCancellationComplaintPostResource as BaseTenderCancellationComplaintPostResource,
)
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE


@optendersresource(
    name="{}:Tender Cancellation Complaint Posts".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Tender cancellation complaint posts",
)
class CompetitiveDialogueEUCancellationComplaintPostResource(
    BaseTenderCancellationComplaintPostResource
):
    pass


@optendersresource(
    name="{}:Tender Cancellation Complaint Posts".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Tender cancellation complaint posts",
)
class CompetitiveDialogueUACancellationComplaintPostResource(
    BaseTenderCancellationComplaintPostResource
):
    pass
