from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.competitivedialogue.procedure.state.stage1.criterion_rg import (
    CDStage1EURequirementGroupState,
    CDStage1UARequirementGroupState,
)
from openprocurement.tender.core.procedure.views.criterion_rg import (
    BaseRequirementGroupResource,
)


@resource(
    name="{}:Criteria Requirement Group".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
    description="Competitive Dialogue EU requirement group",
)
class CDEURequirementGroupResource(BaseRequirementGroupResource):
    state_class = CDStage1EURequirementGroupState


@resource(
    name="{}:Criteria Requirement Group".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    description="Competitive Dialogue UA requirement group",
)
class CDUARequirementGroupResource(BaseRequirementGroupResource):
    state_class = CDStage1UARequirementGroupState
