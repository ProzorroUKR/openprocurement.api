from openprocurement.tender.esco.procedure.state.cancellation import ESCOCancellationState
from openprocurement.tender.openeu.procedure.views.cancellation import EUCancellationResource
from cornice.resource import resource


@resource(
    name="esco:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="esco",
    description="Tender ESCO Cancellations",
)
class ESCOCancellationResource(EUCancellationResource):
    state_class = ESCOCancellationState
