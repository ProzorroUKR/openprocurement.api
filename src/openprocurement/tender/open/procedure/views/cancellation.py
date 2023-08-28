from openprocurement.tender.core.procedure.views.cancellation import BaseCancellationResource
from openprocurement.tender.open.constants import ABOVE_THRESHOLD_GROUP_NAME, ABOVE_THRESHOLD_GROUP
from openprocurement.tender.open.procedure.state.cancellation import OpenCancellationState
from cornice.resource import resource


@resource(
    name=f"{ABOVE_THRESHOLD_GROUP_NAME}:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType=ABOVE_THRESHOLD_GROUP,
    description="Tender cancellations",
)
class CancellationResource(BaseCancellationResource):
    state_class = OpenCancellationState
