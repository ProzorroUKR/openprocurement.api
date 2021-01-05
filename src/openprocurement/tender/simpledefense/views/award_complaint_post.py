# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openuadefense.views.award_complaint_post import (
    TenderAwardComplaintPostResource as BaseTenderAwardComplaintPostResource
)


@optendersresource(
    name="simple.defense:Tender Award Complaint Posts",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType="simple.defense",
    description="Tender award complaint posts",
)
class TenderAwardComplaintPostResource(BaseTenderAwardComplaintPostResource):
    """"""