# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource

from openprocurement.tender.openua.views.complaint_post import (
    TenderComplaintPostResource as BaseTenderComplaintPostResource
)


@optendersresource(
    name="simple.defense:Tender Complaint Posts",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType="simple.defense",
    description="Tender complaint posts",
)
class TenderComplaintPostResource(BaseTenderComplaintPostResource):
    pass
