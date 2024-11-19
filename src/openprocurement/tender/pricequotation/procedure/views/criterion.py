from cornice.resource import resource

from openprocurement.tender.core.procedure.views.criterion import BaseCriterionResource
from openprocurement.tender.pricequotation.constants import PQ
from openprocurement.tender.pricequotation.procedure.state.criterion import (
    PQCriterionState,
)


@resource(
    name=f"{PQ}:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=PQ,
    description=f"{PQ} Tender criteria",
)
class CriterionResource(BaseCriterionResource):
    state_class = PQCriterionState
