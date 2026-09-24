from logging import getLogger

from cornice.resource import resource

from openprocurement.tender.core.procedure.views.bid import TenderBidResource
from openprocurement.tender.openua.procedure.state.bid import OpenUABidState

LOGGER = getLogger(__name__)


@resource(
    name="aboveThresholdUA:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender bids",
)
class OpenUATenderBidResource(TenderBidResource):
    state_class = OpenUABidState
