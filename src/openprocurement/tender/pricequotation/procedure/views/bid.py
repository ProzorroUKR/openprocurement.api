from logging import getLogger

from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.bid import TenderBidResource
from openprocurement.tender.pricequotation.procedure.state.bid import PQBidState

LOGGER = getLogger(__name__)


@resource(
    name=f"{ProcurementMethodType.PRICE_QUOTATION}:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType=ProcurementMethodType.PRICE_QUOTATION,
    description="Tender bids",
)
class PQTenderBidResource(TenderBidResource):
    state_class = PQBidState
