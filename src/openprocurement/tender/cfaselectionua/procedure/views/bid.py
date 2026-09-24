from logging import getLogger

from cornice.resource import resource

from openprocurement.tender.cfaselectionua.procedure.serializers.bid import (
    BidSerializer,
)
from openprocurement.tender.cfaselectionua.procedure.state.bid import CFASelectionBidState
from openprocurement.tender.core.procedure.views.bid import TenderBidResource

LOGGER = getLogger(__name__)


@resource(
    name="closeFrameworkAgreementSelectionUA:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender bids",
)
class CFASelectionTenderBidResource(TenderBidResource):
    serializer_class = BidSerializer
    state_class = CFASelectionBidState
