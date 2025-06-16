from cornice.resource import resource

from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.competitiveordering.procedure.state.lot import (
    CompetitiveOrderingTenderLotState,
)
from openprocurement.tender.core.procedure.views.lot import TenderLotResource


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType=COMPETITIVE_ORDERING,
    description="Tender lots",
)
class COTenderLotResource(TenderLotResource):
    state_class = CompetitiveOrderingTenderLotState
