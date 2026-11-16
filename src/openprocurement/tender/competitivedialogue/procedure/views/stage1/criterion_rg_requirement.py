from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.competitivedialogue.procedure.state.stage1.criterion_rg_requirement import (
    CDStage1EURequirementState,
    CDStage1UARequirementState,
)
from openprocurement.tender.core.procedure.views.criterion_rg_requirement import (
    BaseRequirementResource,
)


@resource(
    name="{}:Requirement Group Requirement".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
    description="Competitive Dialogue EU requirement group requirement",
)
class CDEURequirementResource(BaseRequirementResource):
    state_class = CDStage1EURequirementState


@resource(
    name="{}:Requirement Group Requirement".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    description="Competitive Dialogue UA requirement group requirement",
)
class CDUARequirementResource(BaseRequirementResource):
    state_class = CDStage1UARequirementState
