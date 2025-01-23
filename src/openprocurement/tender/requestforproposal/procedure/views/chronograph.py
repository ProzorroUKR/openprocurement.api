from cornice.resource import resource

from openprocurement.tender.core.procedure.views.chronograph import (
    TenderChronographResource,
)
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RequestForProposalTenderState,
)


@resource(
    name="requestForProposal:Tender Chronograph",
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType="requestForProposal",
    description="Tender chronograph",
)
class RequestForProposalChronographResource(TenderChronographResource):
    state_class = RequestForProposalTenderState
