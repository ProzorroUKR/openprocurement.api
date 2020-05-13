# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.complaint import BaseTenderComplaintResource
from openprocurement.tender.openua.validation import validate_submit_claim_time, validate_update_claim_time


@optendersresource(
    name="aboveThresholdEU:Tender Complaints",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender EU complaints",
)
class TenderEUComplaintResource(BaseTenderComplaintResource):
    def validate_submit_claim_time_method(self, request):
        return validate_submit_claim_time(request)
    
    def validate_update_claim_time_method(self, request):
        return validate_update_claim_time(request)
