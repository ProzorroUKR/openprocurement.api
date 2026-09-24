from logging import getLogger

from cornice.resource import resource

from openprocurement.tender.core.procedure.views.bid import TenderBidResource
from openprocurement.tender.open.constants import ABOVE_THRESHOLD
from openprocurement.tender.open.procedure.state.bid import OpenBidState

LOGGER = getLogger(__name__)


@resource(
    name=f"{ABOVE_THRESHOLD}:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType=ABOVE_THRESHOLD,
    description="Tender bids",
)
class OpenTenderBidResource(TenderBidResource):
    state_class = OpenBidState
