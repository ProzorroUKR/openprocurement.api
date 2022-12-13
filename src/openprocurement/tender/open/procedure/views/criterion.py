from cornice.resource import resource

from openprocurement.tender.open.constants import ABOVE_THRESHOLD
from openprocurement.tender.core.procedure.views.criterion import BaseCriterionResource
from openprocurement.tender.open.procedure.state.criterion import OpenCriterionState


@resource(
    name=f"{ABOVE_THRESHOLD}:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=ABOVE_THRESHOLD,
    description="Tender criteria",
)
class CriterionResource(BaseCriterionResource):
    state_class = OpenCriterionState
