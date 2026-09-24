from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.competitivedialogue.procedure.state.stage2.criterion_rg_requirement import (
    CDStage2RequirementState,
)
from openprocurement.tender.core.procedure.views.criterion_rg_requirement import (
    BaseRequirementResource,
)


class BaseStage2RequirementResource(BaseRequirementResource):
    pass


@resource(
    name="{}:Requirement Group Requirement".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage 2 EU requirement group requirement",
)
class Stage2EURequirementResource(BaseStage2RequirementResource):
    state_class = CDStage2RequirementState


@resource(
    name="{}:Requirement Group Requirement".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue Stage 2 UA requirement group requirement",
)
class Stage2UARequirementResource(BaseStage2RequirementResource):
    state_class = CDStage2RequirementState
