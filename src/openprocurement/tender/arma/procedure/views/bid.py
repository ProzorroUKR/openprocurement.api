from logging import getLogger

from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.arma.procedure.state.bid import ARMABidState
from openprocurement.tender.core.procedure.views.bid import TenderBidResource

LOGGER = getLogger(__name__)


@resource(
    name=f"{COMPLEX_ASSET_ARMA}:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender bids",
)
class BidResource(TenderBidResource):
    state_class = ARMABidState
