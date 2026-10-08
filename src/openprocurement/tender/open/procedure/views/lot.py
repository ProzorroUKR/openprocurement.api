from cornice.resource import resource

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
    SimpleDefenseTenderLotState,
)
from openprocurement.tender.open.procedure.views.base import COStateClass


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
        COMPETITIVE_ORDERING,
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
        SIMPLE_DEFENSE: SimpleDefenseTenderLotState,
        COMPETITIVE_ORDERING: COStateClass(COShortTenderLotState, COLongTenderLotState),
        BELOW_THRESHOLD: BelowThresholdTenderLotState,
        REQUEST_FOR_PROPOSAL: RFPTenderLotState,
    }
