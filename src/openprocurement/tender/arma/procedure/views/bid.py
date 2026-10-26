from logging import getLogger

from cornice.resource import resource

from openprocurement.tender.arma.constants import (
    ARMA_PROCUREMENT_METHOD_TYPES,
    ARMA_ROUTE_PREFIX,
    COMPLEX_ASSET_ARMA,
    SIMPLE_ASSET_ARMA,
)
from openprocurement.tender.arma.procedure.state.bid import (
    ComplexAssetBidState,
    SimpleAssetBidState,
)
from openprocurement.tender.core.procedure.views.bid import TenderBidResource

LOGGER = getLogger(__name__)


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
    description="Tender bids",
)
class BidResource(TenderBidResource):
    state_classes = {
        COMPLEX_ASSET_ARMA: ComplexAssetBidState,
        SIMPLE_ASSET_ARMA: SimpleAssetBidState,
    }
