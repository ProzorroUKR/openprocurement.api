from openprocurement.tender.core.procedure.views.cancellation import BaseCancellationResource
from openprocurement.tender.openua.procedure.state.cancellation import OpenUACancellationState
from cornice.resource import resource


@resource(
    name="aboveThresholdUA:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender cancellations",
)
class UACancellationResource(BaseCancellationResource):
    state_class = OpenUACancellationState
