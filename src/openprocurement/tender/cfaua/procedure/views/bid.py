from logging import getLogger

from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.serializers.bid import BidSerializer
from openprocurement.tender.cfaua.procedure.state.bid import CFAUABidState
from openprocurement.tender.openua.procedure.views.bid import OpenUATenderBidResource

LOGGER = getLogger(__name__)


@resource(
    name="closeFrameworkAgreementUA:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender EU bids",
)
class CFAUATenderBidResource(OpenUATenderBidResource):
    state_class = CFAUABidState
    serializer_class = BidSerializer
