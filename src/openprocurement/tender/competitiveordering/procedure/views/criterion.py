from cornice.resource import resource

from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.competitiveordering.procedure.state.criterion import (
    COCriterionState,
)
from openprocurement.tender.core.procedure.views.criterion import BaseCriterionResource


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=COMPETITIVE_ORDERING,
    description="Tender criteria",
)
class COCriterionResource(BaseCriterionResource):
    state_class = COCriterionState
