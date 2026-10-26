from cornice.resource import resource

from openprocurement.tender.arma.constants import (
    ARMA_PROCUREMENT_METHOD_TYPES,
    ARMA_ROUTE_PREFIX,
    COMPLEX_ASSET_ARMA,
    SIMPLE_ASSET_ARMA,
)
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
    procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
    description="ARMA tenders",
    accept="application/json",
)
class TenderResource(TendersResource):
    serializer_class = TenderBaseSerializer
    state_classes = {
        COMPLEX_ASSET_ARMA: ComplexAssetTenderDetailsState,
        SIMPLE_ASSET_ARMA: SimpleAssetTenderDetailsState,
    }
