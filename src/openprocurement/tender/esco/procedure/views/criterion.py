from cornice.resource import resource

from openprocurement.tender.core.procedure.views.criterion import BaseCriterionResource
from openprocurement.tender.esco.procedure.state.criterion import ESCOCriterionState


@resource(
    name="esco:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType="esco",
    description="Tender criteria",
)
class CriterionResource(BaseCriterionResource):
    state_class = ESCOCriterionState
