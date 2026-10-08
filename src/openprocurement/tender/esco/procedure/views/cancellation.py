from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.mask import TENDER_MASK_MAPPING
from openprocurement.tender.core.procedure.views.cancellation import BaseCancellationResource
from openprocurement.tender.core.utils import context_view
from openprocurement.tender.esco.procedure.serializers.tender import (
    ESCOTenderSerializer,
)
from openprocurement.tender.open.procedure.state.cancellation import AboveThresholdEUCancellationState


@resource(
    name="esco:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="esco",
    description="Tender ESCO Cancellations",
)
class ESCOCancellationResource(BaseCancellationResource):
    state_class = AboveThresholdEUCancellationState

    @json_view(
        permission="view_tender",
    )
    @context_view(
        objs={
            "tender": (ESCOTenderSerializer, TENDER_MASK_MAPPING),
        }
    )
    def get(self):
        return super().get()
