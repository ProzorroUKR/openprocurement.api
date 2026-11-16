from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.arma.constants import ARMA_ROUTE_PREFIX, ARMAProcurementMethodType
from openprocurement.tender.arma.procedure.state.tender_details import (
    ComplexAssetTenderDetailsState,
    SimpleAssetTenderDetailsState,
)
from openprocurement.tender.core.procedure.serializers.tender import (
    TenderBaseSerializer,
)
from openprocurement.tender.core.procedure.views.tender import TendersResource


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType=ARMAProcurementMethodType,
    description="ARMA tenders",
    accept="application/json",
)
class TenderResource(TendersResource):
    serializer_class = TenderBaseSerializer
    state_classes = {
        ProcurementMethodType.COMPLEX_ASSET_ARMA: ComplexAssetTenderDetailsState,
        ProcurementMethodType.SIMPLE_ASSET_ARMA: SimpleAssetTenderDetailsState,
    }
