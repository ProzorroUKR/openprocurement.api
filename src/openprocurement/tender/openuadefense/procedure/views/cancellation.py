from openprocurement.tender.core.procedure.views.cancellation import BaseCancellationResource
from openprocurement.tender.openuadefense.procedure.state.cancellation import UADefenseCancellationState
from cornice.resource import resource


@resource(
    name="aboveThresholdUA.defense:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="aboveThresholdUA.defense",
    description="Tender cancellations",
)
class UaDefenseCancellationResource(BaseCancellationResource):
    state_class = UADefenseCancellationState
