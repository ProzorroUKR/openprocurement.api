from cornice.resource import resource

from openprocurement.tender.arma.constants import (
    ARMA_PROCUREMENT_METHOD_TYPES,
    ARMA_ROUTE_PREFIX,
    COMPLEX_ASSET_ARMA,
    SIMPLE_ASSET_ARMA,
)
from openprocurement.tender.arma.procedure.state.criterion import (
    ComplexAssetCriterionState,
    SimpleAssetCriterionState,
)
from openprocurement.tender.core.procedure.views.criterion import BaseCriterionResource


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
    description="Tender criteria",
)
class CriterionResource(BaseCriterionResource):
    state_classes = {
        COMPLEX_ASSET_ARMA: ComplexAssetCriterionState,
        SIMPLE_ASSET_ARMA: SimpleAssetCriterionState,
    }
