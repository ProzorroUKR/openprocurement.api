# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.openua.validation import (
    validate_complaint_post_complaint_status,
    validate_qualification_complaint_post_data,
    validate_complaint_post,
    validate_complaint_post_review_date,
)
from openprocurement.tender.openua.views.complaint_post import TenderComplaintPostResource


@qualifications_resource(
    name="aboveThresholdEU:Tender Qualification Complaint Posts",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender qualification complaint posts",
)
class TenderQualificationComplaintPostResource(TenderComplaintPostResource):
    def generate_location_url(self):
        return  self.request.route_url(
            "{}:Tender Qualification Complaint Posts".format(self.request.validated["tender"].procurementMethodType),
            tender_id=self.request.validated["tender_id"],
            qualification_id=self.request.validated["qualification_id"],
            complaint_id=self.request.validated["complaint_id"],
            post_id=self.request.validated["post"]["id"],
        )

    @json_view(
        content_type="application/json",
        validators=(
                validate_qualification_complaint_post_data,
                validate_complaint_post,
                validate_complaint_post_complaint_status,
                validate_complaint_post_review_date,
        ),
        permission="edit_complaint",
    )
    def collection_post(self):
        return super(TenderQualificationComplaintPostResource, self).collection_post()
