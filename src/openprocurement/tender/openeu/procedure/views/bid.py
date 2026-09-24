from logging import getLogger

from cornice.resource import resource

from openprocurement.tender.core.procedure.views.bid import TenderBidResource
from openprocurement.tender.openeu.procedure.state.bid import OpenEUBidState

LOGGER = getLogger(__name__)


@resource(
    name="aboveThresholdEU:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender EU bids",
)
class OpenEUTenderBidResource(TenderBidResource):
    state_class = OpenEUBidState
