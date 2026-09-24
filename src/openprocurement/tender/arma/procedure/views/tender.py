from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.arma.procedure.state.tender_details import (
    TenderDetailsState,
)
from openprocurement.tender.core.procedure.serializers.tender import (
    TenderBaseSerializer,
)
from openprocurement.tender.core.procedure.views.tender import TendersResource


@resource(
    name=f"{COMPLEX_ASSET_ARMA}:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="ARMA tenders",
    accept="application/json",
)
class TenderResource(TendersResource):
    serializer_class = TenderBaseSerializer
    state_class = TenderDetailsState
