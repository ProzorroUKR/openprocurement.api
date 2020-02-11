# -*- coding: utf-8 -*-
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.core.utils import optendersresource

from openprocurement.tender.openua.views.complaint_post import (
    TenderComplaintPostResource as BaseTenderComplaintPostResource
)


@optendersresource(
    name="{}:Tender Complaint Posts".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Tender complaint posts",
)
class TenderCompetitiveDialogueEUComplaintPostResource(BaseTenderComplaintPostResource):
    pass


@optendersresource(
    name="{}:Tender Complaint Posts".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Tender complaint posts",
)
class TenderCompetitiveDialogueUAComplaintPostResource(BaseTenderComplaintPostResource):
    pass
