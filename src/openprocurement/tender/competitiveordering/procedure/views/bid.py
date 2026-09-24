from logging import getLogger

from cornice.resource import resource

from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.competitiveordering.procedure.state.bid import COBidState
from openprocurement.tender.core.procedure.views.bid import TenderBidResource

LOGGER = getLogger(__name__)


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType=COMPETITIVE_ORDERING,
    description="Tender bids",
)
class COTenderBidResource(TenderBidResource):
    state_class = COBidState
