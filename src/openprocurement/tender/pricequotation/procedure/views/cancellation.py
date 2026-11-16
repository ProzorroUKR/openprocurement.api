from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.cancellation import (
    BaseCancellationResource,
)
from openprocurement.tender.pricequotation.procedure.state.cancellation import (
    PQCancellationState,
)


@resource(
    name=f"{ProcurementMethodType.PRICE_QUOTATION}:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType=ProcurementMethodType.PRICE_QUOTATION,
    description="Tender cancellations",
)
class PQCancellationResource(BaseCancellationResource):
    state_class = PQCancellationState
