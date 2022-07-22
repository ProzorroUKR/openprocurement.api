from openprocurement.tender.core.procedure.views.cancellation import BaseCancellationResource
from openprocurement.tender.pricequotation.procedure.state.cancellation import PQCancellationState
from openprocurement.tender.pricequotation.constants import PMT
from cornice.resource import resource


@resource(
    name="{}:Tender Cancellations".format(PMT),
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType=PMT,
    description="Tender cancellations",
)
class UACancellationResource(BaseCancellationResource):
    state_class = PQCancellationState
