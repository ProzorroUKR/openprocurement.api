from logging import getLogger

from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.competitivedialogue.procedure.state.bid import CDBidState
from openprocurement.tender.core.procedure.views.bid import TenderBidResource

LOGGER = getLogger(__name__)


@resource(
    name="{}:Tender Bids".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA bids",
)
class CompetitiveDialogueUABidResource(TenderBidResource):
    state_class = CDBidState


@resource(
    name="{}:Tender Bids".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU bids",
)
class CompetitiveDialogueEUBidResource(TenderBidResource):
    state_class = CDBidState
