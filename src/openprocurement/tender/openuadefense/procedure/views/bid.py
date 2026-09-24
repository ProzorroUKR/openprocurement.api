from logging import getLogger

from cornice.resource import resource

from openprocurement.tender.openua.procedure.views.bid import OpenUATenderBidResource
from openprocurement.tender.openuadefense.procedure.state.bid import (
    OpenUADefenseBidState,
)

LOGGER = getLogger(__name__)


@resource(
    name="aboveThresholdUA.defense:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType="aboveThresholdUA.defense",
    description="Tender UA.defense bids",
)
class OpenUADefenseTenderBidResource(OpenUATenderBidResource):
    state_class = OpenUADefenseBidState
