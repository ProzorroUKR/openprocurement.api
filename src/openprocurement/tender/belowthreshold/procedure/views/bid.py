from logging import getLogger

from cornice.resource import resource

from openprocurement.tender.belowthreshold.procedure.state.bid import (
    BelowThresholdBidState,
)
from openprocurement.tender.core.procedure.views.bid import TenderBidResource

LOGGER = getLogger(__name__)


@resource(
    name="belowThreshold:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType="belowThreshold",
    description="Tender bids",
)
class BelowThresholdTenderBidResource(TenderBidResource):
    state_class = BelowThresholdBidState
