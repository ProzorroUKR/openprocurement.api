from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.tender import TendersResource
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX
from openprocurement.tender.open.procedure.state.tender_details import (
    AboveThresholdEUTenderDetailsState,
    AboveThresholdTenderDetailsState,
    AboveThresholdUATenderDetailsState,
    BelowThresholdTenderDetailsState,
    COLongTenderDetailsState,
    COShortTenderDetailsState,
    DefenseTenderDetailsState,
    OpenTenderingEUTenderDetailsState,
    OpenTenderingUATenderDetailsState,
    RFPTenderDetailsState,
    SimpleDefenseTenderDetailsState,
)
from openprocurement.tender.open.procedure.views.base import (
    COStateClass,
    OpenTenderingStateClass,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    description="Tenders",
    accept="application/json",
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
class OpenTendersResource(TendersResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: AboveThresholdTenderDetailsState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: AboveThresholdUATenderDetailsState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdEUTenderDetailsState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingStateClass(
            OpenTenderingUATenderDetailsState, OpenTenderingEUTenderDetailsState
        ),
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE: DefenseTenderDetailsState,
        ProcurementMethodType.SIMPLE_DEFENSE: SimpleDefenseTenderDetailsState,
        ProcurementMethodType.COMPETITIVE_ORDERING: COStateClass(COShortTenderDetailsState, COLongTenderDetailsState),
        ProcurementMethodType.BELOW_THRESHOLD: BelowThresholdTenderDetailsState,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL: RFPTenderDetailsState,
    }
