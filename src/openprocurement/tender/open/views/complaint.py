# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.complaint import (
    BaseTenderComplaintResource,
    BaseTenderClaimResource,
    BaseComplaintGetResource,
)
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.open.constants import ABOVE_THRESHOLD
from openprocurement.tender.open.validation import validate_submit_claim_time, validate_update_claim_time


@optendersresource(
    name=f"{ABOVE_THRESHOLD}:Tender Complaints Get",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=ABOVE_THRESHOLD,
    request_method=["GET"],
    description="Tender complaints get",
)
class TenderUAComplaintGetResource(BaseComplaintGetResource):
    """"""


@optendersresource(
    name=f"{ABOVE_THRESHOLD}:Tender Complaints",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=ABOVE_THRESHOLD,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender complaints",
)
class TenderComplaintResource(BaseTenderComplaintResource):
    """ """


@optendersresource(
    name=f"{ABOVE_THRESHOLD}:Tender Claims",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=ABOVE_THRESHOLD,
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender claims",
)
class TenderClaimResource(BaseTenderClaimResource):
    @staticmethod
    def validate_submit_claim_time_method(request):
        return validate_submit_claim_time(request)

    @staticmethod
    def validate_update_claim_time_method(request):
        return validate_update_claim_time(request)
