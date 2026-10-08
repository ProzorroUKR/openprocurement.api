from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from openprocurement.tender.competitivedialogue.procedure.state.stage2.criterion import (
    CDStage2EUCriterionState,
    CDStage2UACriterionState,
)
from openprocurement.tender.core.procedure.views.criterion import BaseCriterionResource


class BaseStage2CriterionResource(BaseCriterionResource):
    pass


@resource(
    name="{}:Tender Criteria".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage 2 EU criteria",
)
class Stage2EUCriterionResource(BaseStage2CriterionResource):
    state_class = CDStage2EUCriterionState


@resource(
    name="{}:Tender Criteria".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue Stage 2 UA criteria",
)
class Stage2UACriterionResource(BaseStage2CriterionResource):
    state_class = CDStage2UACriterionState
