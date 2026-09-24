from logging import getLogger

from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.competitivedialogue.procedure.state.stage2.bid import (
    CDStage2EUBidState,
    CDStage2UABidState,
)
from openprocurement.tender.openeu.procedure.views.bid import OpenEUTenderBidResource
from openprocurement.tender.openua.procedure.views.bid import OpenUATenderBidResource

LOGGER = getLogger(__name__)


@resource(
    name="{}:Tender Bids".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue  Stage2EU bids",
)
class CompetitiveDialogueStage2EUBidResource(OpenEUTenderBidResource):
    state_class = CDStage2EUBidState


@resource(
    name="{}:Tender Bids".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue Stage2 UA bids",
)
class CompetitiveDialogueStage2UABidResource(OpenUATenderBidResource):
    state_class = CDStage2UABidState
