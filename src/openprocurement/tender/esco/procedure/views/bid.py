from logging import getLogger

from cornice.resource import resource

from openprocurement.tender.core.procedure.views.bid import TenderBidResource
from openprocurement.tender.esco.procedure.serializers.bid import BidSerializer
from openprocurement.tender.esco.procedure.state.bid import ESCOBidState

LOGGER = getLogger(__name__)


@resource(
    name="esco:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType="esco",
    description="Tender ESCO bids",
)
class ESCOTenderBidResource(TenderBidResource):
    state_class = ESCOBidState
    serializer_class = BidSerializer
