from cornice.resource import resource

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
from openprocurement.tender.open.procedure.views.base import COStateClass


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
        COMPETITIVE_ORDERING,
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
        COMPETITIVE_ORDERING: COStateClass(COShortTenderDetailsState, COLongTenderDetailsState),
        BELOW_THRESHOLD: BelowThresholdTenderDetailsState,
        REQUEST_FOR_PROPOSAL: RFPTenderDetailsState,
    }
