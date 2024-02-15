from cornice.resource import resource

from openprocurement.tender.openeu.procedure.views.cancellation import (
    EUCancellationResource,
)


@resource(
    name="esco:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="esco",
    description="Tender ESCO Cancellations",
)
class ESCOCancellationResource(EUCancellationResource):
    pass
