from cornice.resource import resource

from openprocurement.tender.core.procedure.views.claim import TenderClaimResource
from openprocurement.tender.core.procedure.views.complaint import (
    BaseTenderComplaintGetResource,
)
from openprocurement.tender.requestforproposal.procedure.state.claim import (
    RequestForProposalTenderClaimState,
)


@resource(
    name="requestForProposal:Tender Complaints Get",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="requestForProposal",
    request_method=["GET"],
    description="Tender complaints get",
)
class RequestForProposalTenderClaimAndComplaintGetResource(BaseTenderComplaintGetResource):
    pass


@resource(
    name="requestForProposal:Tender Claims",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="requestForProposal",
    request_method=["PATCH"],
    complaintType="claim",
    description="Tender claims",
)
class RequestForProposalTenderClaimResource(TenderClaimResource):
    state_class = RequestForProposalTenderClaimState
