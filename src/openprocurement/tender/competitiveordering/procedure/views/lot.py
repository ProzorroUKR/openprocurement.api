from cornice.resource import resource

from openprocurement.api.procedure.context import get_object
from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.competitiveordering.procedure.state.lot import (
    COLongTenderLotState,
    COShortTenderLotState,
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
    state_class = None
    state_short_class = COShortTenderLotState
    state_long_class = COLongTenderLotState

    def __init__(self, request, context=None):
        self.state_short = self.state_short_class(request)
        self.state_long = self.state_long_class(request)
        super().__init__(request, context)

    @property
    def state(self):
        agreement = get_object("agreement")
        agreement_has_items = bool(agreement.get("items"))
        if agreement_has_items:
            return self.state_short
        else:
            return self.state_long
