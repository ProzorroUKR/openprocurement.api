# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.complaint import (
    BaseTenderComplaintResource,
    BaseTenderClaimResource,
    BaseComplaintGetResource,
)
from openprocurement.tender.openua.validation import validate_submit_claim_time
from openprocurement.tender.core.validation import validate_update_claim_time


@optendersresource(
    name="aboveThresholdEU:Tender Complaints Get",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdEU",
    request_method=["GET"],
    description="Tender EU complaints get",
)
class TenderEUComplaintGetResource(BaseComplaintGetResource):
    """ """


@optendersresource(
    name="aboveThresholdEU:Tender Complaints",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdEU",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender EU complaints",
)
class TenderEUComplaintResource(BaseTenderComplaintResource):
    """ """


@optendersresource(
    name="aboveThresholdEU:Tender Claims",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdEU",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender EU claims",
)
class TenderEUClaimResource(BaseTenderClaimResource):
    def validate_submit_claim_time_method(self, request):
        return validate_submit_claim_time(request)

    def validate_update_claim_time_method(self, request):
        return validate_update_claim_time(request)
