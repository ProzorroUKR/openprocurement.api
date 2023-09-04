from cornice.resource import resource
from openprocurement.tender.core.procedure.views.complaint import BaseTenderComplaintGetResource
from openprocurement.tender.core.procedure.views.claim import TenderClaimResource
from openprocurement.tender.belowthreshold.procedure.state.claim import BelowThresholdTenderClaimState


@resource(
    name="belowThreshold:Tender Complaints Get",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="belowThreshold",
    request_method=["GET"],
    description="Tender complaints get",
)
class BelowThresholdTenderClaimAndComplaintGetResource(BaseTenderComplaintGetResource):
    pass


@resource(
    name="belowThreshold:Tender Claims",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="belowThreshold",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender claims",
)
class BelowThresholdTenderClaimResource(TenderClaimResource):
    state_class = BelowThresholdTenderClaimState
