from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.arma.constants import ARMA_ROUTE_PREFIX, ARMAProcurementMethodType
from openprocurement.tender.arma.procedure.state.criterion import (
    ComplexAssetCriterionState,
    SimpleAssetCriterionState,
)
from openprocurement.tender.core.procedure.views.criterion import BaseCriterionResource


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=ARMAProcurementMethodType,
    description="Tender criteria",
)
class CriterionResource(BaseCriterionResource):
    state_classes = {
        ProcurementMethodType.COMPLEX_ASSET_ARMA: ComplexAssetCriterionState,
        ProcurementMethodType.SIMPLE_ASSET_ARMA: SimpleAssetCriterionState,
    }
