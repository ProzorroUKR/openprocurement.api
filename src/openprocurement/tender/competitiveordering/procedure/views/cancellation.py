from cornice.resource import resource

from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.competitiveordering.procedure.state.cancellation import (
    OpenCancellationState,
)
from openprocurement.tender.core.procedure.views.cancellation import (
    BaseCancellationResource,
)


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType=COMPETITIVE_ORDERING,
    description="Tender cancellations",
)
class CancellationResource(BaseCancellationResource):
    state_class = OpenCancellationState
