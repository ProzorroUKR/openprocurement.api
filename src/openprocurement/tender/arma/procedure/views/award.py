from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.arma.constants import ARMA_ROUTE_PREFIX, ARMAProcurementMethodType
from openprocurement.tender.arma.procedure.state.award import (
    ComplexAssetAwardState,
    SimpleAssetAwardState,
)
from openprocurement.tender.core.procedure.views.award import TenderAwardResource


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType=ARMAProcurementMethodType,
)
class AwardResource(TenderAwardResource):
    state_classes = {
        ProcurementMethodType.COMPLEX_ASSET_ARMA: ComplexAssetAwardState,
        ProcurementMethodType.SIMPLE_ASSET_ARMA: SimpleAssetAwardState,
    }
