from cornice.resource import resource

from openprocurement.tender.core.procedure.views.tender import TendersResource
from openprocurement.tender.esco.procedure.serializers.tender import (
    ESCOTenderSerializer,
)
from openprocurement.tender.esco.procedure.state.tender_details import (
    ESCOTenderDetailsState,
)


@resource(
    name="esco:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType="esco",
    description="esco tenders",
    accept="application/json",
)
class ESCOTenderResource(TendersResource):
    serializer_class = ESCOTenderSerializer
    state_class = ESCOTenderDetailsState
