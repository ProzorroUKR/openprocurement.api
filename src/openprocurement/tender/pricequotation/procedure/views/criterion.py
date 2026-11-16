from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.criterion import BaseCriterionResource
from openprocurement.tender.pricequotation.procedure.state.criterion import (
    PQCriterionState,
)


@resource(
    name=f"{ProcurementMethodType.PRICE_QUOTATION}:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=ProcurementMethodType.PRICE_QUOTATION,
    description=f"{ProcurementMethodType.PRICE_QUOTATION} Tender criteria",
)
class CriterionResource(BaseCriterionResource):
    state_class = PQCriterionState
