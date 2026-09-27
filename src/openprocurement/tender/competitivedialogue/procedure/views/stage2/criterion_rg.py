from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from openprocurement.tender.competitivedialogue.procedure.state.stage2.criterion_rg import (
    CDStage2EURequirementGroupState,
    CDStage2UARequirementGroupState,
)
from openprocurement.tender.core.procedure.views.criterion_rg import (
    BaseRequirementGroupResource,
)


class BaseStage2RequirementGroupResource(BaseRequirementGroupResource):
    pass


@resource(
    name="{}:Criteria Requirement Group".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage 2 EU requirement group",
)
class Stage2EURequirementGroupResource(BaseStage2RequirementGroupResource):
    state_class = CDStage2EURequirementGroupState


@resource(
    name="{}:Criteria Requirement Group".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue Stage 2 UA requirement group",
)
class Stage2UARequirementGroupResource(BaseStage2RequirementGroupResource):
    state_class = CDStage2UARequirementGroupState
