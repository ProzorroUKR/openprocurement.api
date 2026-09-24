from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.mask import TENDER_MASK_MAPPING
from openprocurement.tender.core.procedure.views.award import TenderAwardResource
from openprocurement.tender.core.utils import context_view
from openprocurement.tender.esco.procedure.serializers.award import AwardSerializer
from openprocurement.tender.esco.procedure.serializers.tender import (
    ESCOTenderSerializer,
)
from openprocurement.tender.esco.procedure.state.award import AwardState


@resource(
    name="esco:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender ESCO Awards",
    procurementMethodType="esco",
)
class EUTenderAwardResource(TenderAwardResource):
    serializer_class = AwardSerializer
    state_class = AwardState

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
