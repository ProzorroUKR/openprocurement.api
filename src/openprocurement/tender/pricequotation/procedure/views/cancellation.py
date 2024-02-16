from cornice.resource import resource

from openprocurement.tender.core.procedure.views.cancellation import (
    BaseCancellationResource,
)
from openprocurement.tender.pricequotation.constants import PQ
from openprocurement.tender.pricequotation.procedure.state.cancellation import (
    PQCancellationState,
)


@resource(
    name="{}:Tender Cancellations".format(PQ),
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType=PQ,
    description="Tender cancellations",
)
class UACancellationResource(BaseCancellationResource):
    state_class = PQCancellationState
