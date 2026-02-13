from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.arma.procedure.state.criterion import CriterionState
from openprocurement.tender.core.procedure.views.criterion import BaseCriterionResource


@resource(
    name="complexAsset.arma:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender criteria",
)
class CriterionResource(BaseCriterionResource):
    state_class = CriterionState
