from cornice.resource import resource
from openprocurement.tender.core.procedure.views.complaint import (
    BaseTenderComplaintGetResource,
    TenderComplaintResource,
)
from openprocurement.tender.core.procedure.views.claim import TenderClaimResource
from openprocurement.tender.openua.procedure.state.claim import OpenUATenderClaimState
from openprocurement.tender.openua.procedure.state.complaint import OpenUATenderComplaintState


@resource(
    name="aboveThresholdUA:Tender Complaints Get",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA",
    request_method=["GET"],
    description="Tender complaints get",
)
class OpenUATenderClaimAndComplaintGetResource(BaseTenderComplaintGetResource):
    pass


@resource(
    name="aboveThresholdUA:Tender Claims",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender claims",
)
class OpenUATenderClaimResource(TenderClaimResource):
    state_class = OpenUATenderClaimState


@resource(
    name="aboveThresholdUA:Tender Complaints",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender complaints",
)
class OpenUATenderComplaintResource(TenderComplaintResource):
    state_class = OpenUATenderComplaintState

