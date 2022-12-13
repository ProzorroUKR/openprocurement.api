from cornice.resource import resource

from openprocurement.tender.core.procedure.views.criterion import BaseCriterionResource
from openprocurement.tender.openeu.procedure.state.criterion import OpenEUCriterionState


@resource(
    name="aboveThresholdEU:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender criteria",
)
class CriterionResource(BaseCriterionResource):
    state_class = OpenEUCriterionState
