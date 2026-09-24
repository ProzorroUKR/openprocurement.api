from cornice.resource import resource

from openprocurement.api.procedure.context import get_object
from openprocurement.tender.core.procedure.views.lot import TenderLotResource
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD,
    ABOVE_THRESHOLD_EU,
    ABOVE_THRESHOLD_UA,
    ABOVE_THRESHOLD_UA_DEFENSE,
    BELOW_THRESHOLD,
    COMPETITIVE_ORDERING,
    OPEN_ROUTE_PREFIX,
    REQUEST_FOR_PROPOSAL,
    SIMPLE_DEFENSE,
)
from openprocurement.tender.open.procedure.state.lot import (
    AboveThresholdEUTenderLotState,
    AboveThresholdTenderLotState,
    AboveThresholdUATenderLotState,
    BelowThresholdTenderLotState,
    COLongTenderLotState,
    COShortTenderLotState,
    DefenseTenderLotState,
    RFPTenderLotState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    description="Tender lots",
    procurementMethodType=[
        ABOVE_THRESHOLD,
        ABOVE_THRESHOLD_UA,
        ABOVE_THRESHOLD_EU,
        ABOVE_THRESHOLD_UA_DEFENSE,
        SIMPLE_DEFENSE,
        BELOW_THRESHOLD,
        REQUEST_FOR_PROPOSAL,
    ],
)
class OpenTenderLotResource(TenderLotResource):
    state_classes = {
        ABOVE_THRESHOLD: AboveThresholdTenderLotState,
        ABOVE_THRESHOLD_UA: AboveThresholdUATenderLotState,
        ABOVE_THRESHOLD_EU: AboveThresholdEUTenderLotState,
        ABOVE_THRESHOLD_UA_DEFENSE: DefenseTenderLotState,
        SIMPLE_DEFENSE: DefenseTenderLotState,
        BELOW_THRESHOLD: BelowThresholdTenderLotState,
        REQUEST_FOR_PROPOSAL: RFPTenderLotState,
    }


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Lots (competitiveOrdering)",
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
