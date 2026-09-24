from cornice.resource import resource

from openprocurement.tender.core.procedure.serializers.tender import (
    TenderBaseSerializer,
)
from openprocurement.tender.core.procedure.views.tender import TendersResource
from openprocurement.tender.openeu.procedure.state.tender_details import (
    OpenEUTenderDetailsState,
)


@resource(
    name="aboveThresholdEU:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType="aboveThresholdEU",
    description="aboveThresholdEU tenders",
    accept="application/json",
)
class AboveThresholdEUTenderResource(TendersResource):
    serializer_class = TenderBaseSerializer
    state_class = OpenEUTenderDetailsState
