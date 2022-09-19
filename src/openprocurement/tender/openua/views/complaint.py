# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.complaint import (
    BaseTenderComplaintResource,
    BaseTenderClaimResource,
    BaseComplaintGetResource,
)
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.validation import validate_submit_claim_time
from openprocurement.tender.core.validation import validate_update_claim_time


@optendersresource(
    name="aboveThresholdUA:Tender Complaints Get",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA",
    request_method=["GET"],
    description="Tender complaints get",
)
class TenderUAComplaintGetResource(BaseComplaintGetResource):
    """"""


@optendersresource(
    name="aboveThresholdUA:Tender Complaints",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender complaints",
)
class TenderUAComplaintResource(BaseTenderComplaintResource):
    """ """


@optendersresource(
    name="aboveThresholdUA:Tender Claims",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender claims",
)
class TenderUAClaimResource(BaseTenderClaimResource):
    @staticmethod
    def validate_submit_claim_time_method(request):
        return validate_submit_claim_time(request)

    @staticmethod
    def validate_update_claim_time_method(request):
        return validate_update_claim_time(request)
