from cornice.resource import resource

from openprocurement.tender.arma.constants import (
    ARMA_PROCUREMENT_METHOD_TYPES,
    ARMA_ROUTE_PREFIX,
    COMPLEX_ASSET_ARMA,
    SIMPLE_ASSET_ARMA,
)
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
    procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
)
class AwardResource(TenderAwardResource):
    state_classes = {
        COMPLEX_ASSET_ARMA: ComplexAssetAwardState,
        SIMPLE_ASSET_ARMA: SimpleAssetAwardState,
    }
