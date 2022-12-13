from cornice.resource import resource

from openprocurement.tender.core.procedure.views.criterion import BaseCriterionResource
from openprocurement.tender.openua.procedure.state.criterion import OpenUACriterionState


@resource(
    name="aboveThresholdUA:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender criteria",
)
class CriterionResource(BaseCriterionResource):
    state_class = OpenUACriterionState
