from cornice.resource import resource

from openprocurement.tender.core.procedure.views.cancellation import BaseCancellationResource
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD,
    ABOVE_THRESHOLD_EU,
    ABOVE_THRESHOLD_UA,
    ABOVE_THRESHOLD_UA_DEFENSE,
    BELOW_THRESHOLD,
    COMPETITIVE_ORDERING,
    OPEN_PROCUREMENT_METHOD_TYPES,
    OPEN_ROUTE_PREFIX,
    REQUEST_FOR_PROPOSAL,
    SIMPLE_DEFENSE,
)
from openprocurement.tender.open.procedure.state.cancellation import (
    AboveThresholdCancellationState,
    AboveThresholdEUCancellationState,
    AboveThresholdUACancellationState,
    BelowThresholdCancellationState,
    COCancellationState,
    DefenseCancellationState,
    RFPCancellationState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    description="Tender cancellations",
    procurementMethodType=OPEN_PROCUREMENT_METHOD_TYPES,
)
class OpenBaseCancellationResource(BaseCancellationResource):
    state_classes = {
        ABOVE_THRESHOLD: AboveThresholdCancellationState,
        ABOVE_THRESHOLD_UA: AboveThresholdUACancellationState,
        ABOVE_THRESHOLD_EU: AboveThresholdEUCancellationState,
        ABOVE_THRESHOLD_UA_DEFENSE: DefenseCancellationState,
        SIMPLE_DEFENSE: DefenseCancellationState,
        COMPETITIVE_ORDERING: COCancellationState,
        BELOW_THRESHOLD: BelowThresholdCancellationState,
        REQUEST_FOR_PROPOSAL: RFPCancellationState,
    }
