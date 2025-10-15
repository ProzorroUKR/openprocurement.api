from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.competitivedialogue.procedure.state.criterion_rg_requirement import (
    CDRequirementState,
)
from openprocurement.tender.core.procedure.views.criterion_rg_requirement import (
    BaseRequirementResource,
)


@resource(
    name="{}:Requirement Group Requirement".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU requirement group requirement",
)
class CDEURequirementResource(BaseRequirementResource):
    state_class = CDRequirementState


@resource(
    name="{}:Requirement Group Requirement".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA requirement group requirement",
)
class CDUARequirementResource(BaseRequirementResource):
    state_class = CDRequirementState
