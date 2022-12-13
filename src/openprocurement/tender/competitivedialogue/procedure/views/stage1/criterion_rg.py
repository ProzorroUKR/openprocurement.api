from typing import List, Tuple

from cornice.resource import resource
from pyramid.security import Allow

from openprocurement.tender.core.procedure.views.criterion_rg import BaseRequirementGroupResource
from openprocurement.tender.competitivedialogue.procedure.state.criterion_rg import CDRequirementGroupState
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE


class BaseCDRequirementGroupResource(BaseRequirementGroupResource):
    def __acl__(self) -> List[Tuple[str, str, str]]:
        acl = super().__acl__()
        acl.extend([
            (Allow, "g:competitive_dialogue", "create_rg"),
            (Allow, "g:competitive_dialogue", "edit_rg"),
        ])
        return acl


@resource(
    name="{}:Criteria Requirement Group".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU requirement group",
)
class CDEURequirementGroupResource(BaseCDRequirementGroupResource):
    state_class = CDRequirementGroupState


@resource(
    name="{}:Criteria Requirement Group".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA requirement group",
)
class CDUARequirementGroupResource(BaseCDRequirementGroupResource):
    state_class = CDRequirementGroupState
