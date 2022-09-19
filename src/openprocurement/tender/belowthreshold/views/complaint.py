# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view

from openprocurement.tender.core.views.complaint import BaseTenderClaimResource
from openprocurement.tender.core.views.complaint import BaseComplaintGetResource
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.validation import (
    validate_complaint_data, validate_patch_complaint_data,
    validate_update_claim_time,
)

from openprocurement.tender.belowthreshold.validation import (
    validate_update_complaint_not_in_allowed_status,
    validate_add_complaint_not_in_allowed_tender_status,
    validate_update_complaint_not_in_allowed_tender_status, validate_submit_complaint_time,
)


@optendersresource(
    name="belowThreshold:Tender Complaints Get",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="belowThreshold",
    request_method=["GET"],
    description="Tender complaints get",
)
class TenderComplaintGetResource(BaseComplaintGetResource):
    """ """


@optendersresource(
    name="belowThreshold:Tender Claims",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="belowThreshold",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender claims",
)
class TenderClaimResource(BaseTenderClaimResource):

    patch_check_tender_excluded_statuses = (
        "draft", "claim", "answered",
    )
    patch_as_complaint_owner_tender_statuses = (
        "active.enquiries", "active.tendering",
    )

    @json_view(
        content_type="application/json",
        validators=(
            validate_complaint_data,
            validate_add_complaint_not_in_allowed_tender_status
        ),
        permission="create_complaint",
    )
    def collection_post(self):
        """Post a complaint
        """
        return super(TenderClaimResource, self).collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_complaint_data,
            validate_update_complaint_not_in_allowed_tender_status,
            validate_update_complaint_not_in_allowed_status,
        ),
        permission="edit_complaint",
    )
    def patch(self):
        return super(TenderClaimResource, self).patch()

    @staticmethod
    def validate_submit_claim_time_method(request):
        return validate_submit_complaint_time(request)

    @staticmethod
    def validate_update_claim_time_method(request):
        return validate_update_claim_time(request)

    def check_satisfied(self, data):
        satisfied = data.get("satisfied", self.context.satisfied)
        return isinstance(satisfied, bool)
