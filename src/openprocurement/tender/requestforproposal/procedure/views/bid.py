from logging import getLogger

from cornice.resource import resource

from openprocurement.tender.core.procedure.views.bid import TenderBidResource
from openprocurement.tender.requestforproposal.procedure.state.bid import (
    RequestForProposalBidState,
)

LOGGER = getLogger(__name__)


@resource(
    name="requestForProposal:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType="requestForProposal",
    description="Tender bids",
)
class RequestForProposalTenderBidResource(TenderBidResource):
    state_class = RequestForProposalBidState
