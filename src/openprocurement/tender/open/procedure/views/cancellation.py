from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.cancellation import BaseCancellationResource
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX, OpenProcurementMethodType
from openprocurement.tender.open.procedure.state.cancellation import (
    AboveThresholdCancellationState,
    AboveThresholdEUCancellationState,
    AboveThresholdUACancellationState,
    BelowThresholdCancellationState,
    COCancellationState,
    DefenseCancellationState,
    OpenTenderingCancellationState,
    RFPCancellationState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    description="Tender cancellations",
    procurementMethodType=OpenProcurementMethodType,
)
class OpenBaseCancellationResource(BaseCancellationResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: AboveThresholdCancellationState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: AboveThresholdUACancellationState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdEUCancellationState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingCancellationState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE: DefenseCancellationState,
        ProcurementMethodType.SIMPLE_DEFENSE: DefenseCancellationState,
        ProcurementMethodType.COMPETITIVE_ORDERING: COCancellationState,
        ProcurementMethodType.BELOW_THRESHOLD: BelowThresholdCancellationState,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL: RFPCancellationState,
    }
