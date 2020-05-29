# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.validation import (
    validate_award_complaint_post_data,
    validate_complaint_post,
    validate_complaint_post_complaint_status,
)
from openprocurement.tender.openua.views.award_complaint_post import (
    TenderAwardComplaintPostResource as BaseTenderAwardComplaintPostResource
)
from openprocurement.tender.openuadefense.validation import validate_complaint_post_review_date


@optendersresource(
    name="aboveThresholdUA.defense:Tender Award Complaint Posts",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType="aboveThresholdUA.defense",
    description="Tender award complaint posts",
)
class TenderAwardComplaintPostResource(BaseTenderAwardComplaintPostResource):
    @json_view(
        content_type="application/json",
        validators=(
            validate_award_complaint_post_data,
            validate_complaint_post,
            validate_complaint_post_complaint_status,
            validate_complaint_post_review_date,
        ),
        permission="edit_complaint",
    )
    def collection_post(self):
        return super(TenderAwardComplaintPostResource, self).collection_post()
