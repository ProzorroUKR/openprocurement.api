from logging import getLogger

from cornice.resource import resource

from openprocurement.tender.core.procedure.views.bid import TenderBidResource
from openprocurement.tender.pricequotation.constants import PQ
from openprocurement.tender.pricequotation.procedure.state.bid import PQBidState

LOGGER = getLogger(__name__)


@resource(
    name=f"{PQ}:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType=PQ,
    description="Tender bids",
)
class PQTenderBidResource(TenderBidResource):
    state_class = PQBidState
