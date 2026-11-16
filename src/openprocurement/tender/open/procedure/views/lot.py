from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.lot import TenderLotResource
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX
from openprocurement.tender.open.procedure.state.lot import (
    AboveThresholdEUTenderLotState,
    AboveThresholdTenderLotState,
    AboveThresholdUATenderLotState,
    BelowThresholdTenderLotState,
    COLongTenderLotState,
    COShortTenderLotState,
    DefenseTenderLotState,
    OpenTenderingEUTenderLotState,
    OpenTenderingUATenderLotState,
    RFPTenderLotState,
    SimpleDefenseTenderLotState,
)
from openprocurement.tender.open.procedure.views.base import (
    COStateClass,
    OpenTenderingStateClass,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    description="Tender lots",
    procurementMethodType=[
        ProcurementMethodType.ABOVE_THRESHOLD,
        ProcurementMethodType.ABOVE_THRESHOLD_UA,
        ProcurementMethodType.ABOVE_THRESHOLD_EU,
        ProcurementMethodType.OPEN_TENDERING,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE,
        ProcurementMethodType.SIMPLE_DEFENSE,
        ProcurementMethodType.COMPETITIVE_ORDERING,
        ProcurementMethodType.BELOW_THRESHOLD,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL,
    ],
)
class OpenTenderLotResource(TenderLotResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: AboveThresholdTenderLotState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: AboveThresholdUATenderLotState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdEUTenderLotState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingStateClass(
            OpenTenderingUATenderLotState, OpenTenderingEUTenderLotState
        ),
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE: DefenseTenderLotState,
        ProcurementMethodType.SIMPLE_DEFENSE: SimpleDefenseTenderLotState,
        ProcurementMethodType.COMPETITIVE_ORDERING: COStateClass(COShortTenderLotState, COLongTenderLotState),
        ProcurementMethodType.BELOW_THRESHOLD: BelowThresholdTenderLotState,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL: RFPTenderLotState,
    }
