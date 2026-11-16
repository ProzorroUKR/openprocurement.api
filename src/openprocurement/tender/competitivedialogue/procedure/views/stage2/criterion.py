from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.competitivedialogue.procedure.state.stage2.criterion import (
    CDStage2EUCriterionState,
    CDStage2UACriterionState,
)
from openprocurement.tender.core.procedure.views.criterion import BaseCriterionResource


class BaseStage2CriterionResource(BaseCriterionResource):
    pass


@resource(
    name="{}:Tender Criteria".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2),
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
    description="Competitive Dialogue Stage 2 EU criteria",
)
class Stage2EUCriterionResource(BaseStage2CriterionResource):
    state_class = CDStage2EUCriterionState


@resource(
    name="{}:Tender Criteria".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2),
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2,
    description="Competitive Dialogue Stage 2 UA criteria",
)
class Stage2UACriterionResource(BaseStage2CriterionResource):
    state_class = CDStage2UACriterionState
