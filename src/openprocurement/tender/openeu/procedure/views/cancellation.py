from openprocurement.tender.core.procedure.views.cancellation import BaseCancellationResource
from openprocurement.tender.openeu.procedure.state.cancellation import OpenEUCancellationState
from cornice.resource import resource


@resource(
    name="aboveThresholdEU:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender cancellations",
)
class EUCancellationResource(BaseCancellationResource):
    state_class = OpenEUCancellationState
