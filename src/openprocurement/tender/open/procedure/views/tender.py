from cornice.resource import resource

from openprocurement.api.procedure.context import get_object
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.views.tender import TendersResource
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
from openprocurement.tender.open.procedure.state.tender_details import (
    AboveThresholdEUTenderDetailsState,
    AboveThresholdTenderDetailsState,
    AboveThresholdUATenderDetailsState,
    BelowThresholdTenderDetailsState,
    COLongTenderDetailsState,
    COShortTenderDetailsState,
    DefenseTenderDetailsState,
    RFPTenderDetailsState,
    SimpleDefenseTenderDetailsState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    description="Tenders",
    accept="application/json",
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
class OpenTendersResource(TendersResource):
    state_classes = {
        ABOVE_THRESHOLD: AboveThresholdTenderDetailsState,
        ABOVE_THRESHOLD_UA: AboveThresholdUATenderDetailsState,
        ABOVE_THRESHOLD_EU: AboveThresholdEUTenderDetailsState,
        ABOVE_THRESHOLD_UA_DEFENSE: DefenseTenderDetailsState,
        SIMPLE_DEFENSE: SimpleDefenseTenderDetailsState,
        BELOW_THRESHOLD: BelowThresholdTenderDetailsState,
        REQUEST_FOR_PROPOSAL: RFPTenderDetailsState,
    }


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tenders (competitiveOrdering)",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType=COMPETITIVE_ORDERING,
    description="Tenders",
    accept="application/json",
)
class COTenderResource(TendersResource):
    state_class = None
    state_short_class = COShortTenderDetailsState
    state_long_class = COLongTenderDetailsState

    def __init__(self, request, context=None):
        self.state_short = self.state_short_class(request)
        self.state_long = self.state_long_class(request)
        super().__init__(request, context)

    @property
    def state(self):
        agreement = get_object("agreement")
        if not agreement:
            if "tender" not in self.request.validated:
                # POST: the agreement is fetched in collection_post, the request validation doesn't depend on it
                return self.state_long
            raise_operation_error(self.request, "Agreement not provided or not exist", status=422, name="agreements")
        agreement_has_items = bool(agreement.get("items"))
        if agreement_has_items:
            return self.state_short
        else:
            return self.state_long
