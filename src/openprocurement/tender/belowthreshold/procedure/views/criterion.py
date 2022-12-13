from cornice.resource import resource

from openprocurement.tender.core.procedure.views.criterion import BaseCriterionResource
from openprocurement.tender.belowthreshold.procedure.state.criterion import BelowThresholdCriterionState


@resource(
    name="belowThreshold:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType="belowThreshold",
    description="Tender criteria",
)
class CriterionResource(BaseCriterionResource):
    state_class = BelowThresholdCriterionState
