from cornice.resource import resource

from openprocurement.tender.belowthreshold.procedure.state.cancellation import (
    BelowThresholdCancellationState,
)
from openprocurement.tender.core.procedure.views.cancellation import (
    BaseCancellationResource,
)


@resource(
    name="belowThreshold:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="belowThreshold",
    description="Tender cancellations",
)
class CancellationResource(BaseCancellationResource):
    state_class = BelowThresholdCancellationState
