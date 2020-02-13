# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.complaint import BaseTenderComplaintResource
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.validation import validate_submit_claim_time, validate_update_claim_time


@optendersresource(
    name="aboveThresholdUA:Tender Complaints",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender complaints",
)
class TenderUaComplaintResource(BaseTenderComplaintResource):
    @staticmethod
    def validate_submit_claim_time_method(request):
        return validate_submit_claim_time(request)
    
    @staticmethod
    def validate_update_claim_time_method(request):
        return validate_update_claim_time(request)
