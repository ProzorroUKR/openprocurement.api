from cornice.resource import resource

from openprocurement.tender.core.procedure.views.tender import TendersResource
from openprocurement.tender.requestforproposal.constants import REQUEST_FOR_PROPOSAL
from openprocurement.tender.requestforproposal.procedure.state.tender_details import (
    RFPTenderDetailsState,
)


@resource(
    name=f"{REQUEST_FOR_PROPOSAL}:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType=REQUEST_FOR_PROPOSAL,
    description="RequestForProposal tenders",
    accept="application/json",
)
class RequestForProposalTenderResource(TendersResource):
    state_class = RFPTenderDetailsState
