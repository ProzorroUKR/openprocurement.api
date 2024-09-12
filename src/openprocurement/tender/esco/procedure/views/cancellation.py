from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.tender.core.utils import context_view
from openprocurement.tender.esco.procedure.serializers.tender import (
    ESCOTenderSerializer,
)
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

    @json_view(
        permission="view_tender",
    )
    @context_view(
        objs={
            "tender": ESCOTenderSerializer,
        }
    )
    def get(self):
        return super().get()
