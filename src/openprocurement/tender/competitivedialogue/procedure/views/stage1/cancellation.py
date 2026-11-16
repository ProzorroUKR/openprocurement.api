from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.mask import TENDER_MASK_MAPPING
from openprocurement.tender.core.procedure.serializers.tender import (
    TenderBaseSerializer,
)
from openprocurement.tender.core.procedure.views.cancellation import BaseCancellationResource
from openprocurement.tender.core.utils import context_view
from openprocurement.tender.open.procedure.state.cancellation import AboveThresholdEUCancellationState


@resource(
    name="{}:Tender Cancellations".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU),
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
    description="Competitive Dialogue UE cancellations",
)
class CDEUCancellationResource(BaseCancellationResource):
    state_class = AboveThresholdEUCancellationState

    @json_view(
        permission="view_tender",
    )
    @context_view(
        objs={
            "tender": (TenderBaseSerializer, TENDER_MASK_MAPPING),
        }
    )
    def get(self):
        return super().get()


@resource(
    name="{}:Tender Cancellations".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA),
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    description="Competitive Dialogue UA cancellations",
)
class CDUACancellationResource(CDEUCancellationResource):
    pass
