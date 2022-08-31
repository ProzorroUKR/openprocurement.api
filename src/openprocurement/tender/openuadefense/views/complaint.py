# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.complaint import (
    BaseTenderComplaintResource,
    BaseTenderClaimResource,
    BaseComplaintGetResource,
)

from openprocurement.api.utils import get_now, get_first_revision_date
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.validation import validate_update_claim_time
from openprocurement.tender.openuadefense.validation import validate_submit_claim_time, validate_submit_complaint_time


@optendersresource(
    name="aboveThresholdUA.defense:Tender Complaints Get",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA.defense",
    request_method=["GET"],
    description="Tender complaints get",
)
class TenderUaComplaintGetResource(BaseComplaintGetResource):
    """"""


@optendersresource(
    name="aboveThresholdUA.defense:Tender Complaints",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA.defense",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender complaints",
)
class TenderUaComplaintResource(BaseTenderComplaintResource):
    patch_check_tender_excluded_statuses = (
        "draft", "pending", "accepted", "stopping",
    )

    @staticmethod
    def validate_submit_claim_time_method(request):
        return validate_submit_claim_time(request)

    def pre_create(self):
        tender = self.request.validated["tender"]
        old_rules = get_first_revision_date(tender) < RELEASE_2020_04_19

        complaint = self.request.validated["complaint"]
        if old_rules and complaint.status == "pending":
            self.validate_submit_claim_time_method(self.request)
            complaint.dateSubmitted = get_now()
        else:
            complaint.status = "draft"

        return complaint


@optendersresource(
    name="aboveThresholdUA.defense:Tender Claims",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA.defense",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender claims",
)
class TenderUaClaimResource(BaseTenderClaimResource):

    patch_check_tender_excluded_statuses = (
         "draft", "claim", "answered"
    )
    
    @staticmethod
    def validate_submit_claim_time_method(request):
        return validate_submit_claim_time(request)

    @staticmethod
    def validate_update_claim_time_method(request):
        return validate_update_claim_time(request)

    def pre_create(self):
        complaint = self.request.validated["complaint"]
        if complaint.status == "claim":
            self.validate_submit_claim_time_method(self.request)
        else:
            validate_submit_complaint_time(self.request)
            complaint.status = "draft"
        
        return complaint
