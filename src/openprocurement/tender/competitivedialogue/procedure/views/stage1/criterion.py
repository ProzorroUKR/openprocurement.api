from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.competitivedialogue.procedure.state.stage1.criterion import (
    CDStage1EUCriterionState,
    CDStage1UACriterionState,
)
from openprocurement.tender.core.procedure.views.criterion import BaseCriterionResource


@resource(
    name="{}:Tender Criteria".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU),
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
    description="Competitive Dialogue EU criteria",
)
class CDEUCriterionResource(BaseCriterionResource):
    state_class = CDStage1EUCriterionState


@resource(
    name="{}:Tender Criteria".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA),
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    description="Competitive Dialogue UA criteria",
)
class CDUACriterionResource(BaseCriterionResource):
    state_class = CDStage1UACriterionState
