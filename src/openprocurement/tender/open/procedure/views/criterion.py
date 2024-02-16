from cornice.resource import resource

from openprocurement.tender.core.procedure.views.criterion import BaseCriterionResource
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD_GROUP,
    ABOVE_THRESHOLD_GROUP_NAME,
)
from openprocurement.tender.open.procedure.state.criterion import OpenCriterionState


@resource(
    name=f"{ABOVE_THRESHOLD_GROUP_NAME}:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=ABOVE_THRESHOLD_GROUP,
    description="Tender criteria",
)
class CriterionResource(BaseCriterionResource):
    state_class = OpenCriterionState
