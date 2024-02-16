from cornice.resource import resource

from openprocurement.tender.core.procedure.views.claim import TenderClaimResource
from openprocurement.tender.core.procedure.views.complaint import (
    BaseTenderComplaintGetResource,
    TenderComplaintResource,
)
from openprocurement.tender.openuadefense.procedure.state.claim import (
    OpenUADefenseTenderClaimState,
)
from openprocurement.tender.openuadefense.procedure.state.complaint import (
    OpenUADefenseTenderComplaintState,
)


@resource(
    name="aboveThresholdUA.defense:Tender Complaints Get",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA.defense",
    request_method=["GET"],
    description="Tender complaints get",
)
class OpenUADefenseTenderClaimAndComplaintGetResource(BaseTenderComplaintGetResource):
    pass


@resource(
    name="aboveThresholdUA.defense:Tender Claims",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA.defense",
    request_method=["PATCH"],
    complaintType="claim",
    description="Tender claims",
)
class OpenUADefenseTenderClaimResource(TenderClaimResource):
    state_class = OpenUADefenseTenderClaimState


@resource(
    name="aboveThresholdUA.defense:Tender Complaints",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA.defense",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender complaints",
)
class OpenUADefenseTenderComplaintResource(TenderComplaintResource):
    state_class = OpenUADefenseTenderComplaintState
