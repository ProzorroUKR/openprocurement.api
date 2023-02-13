from typing import Optional, List, Tuple

from cornice.resource import resource
from pyramid.security import Allow

from openprocurement.api.utils import json_view
from openprocurement.tender.competitivedialogue.procedure.views.stage1.criterion_rg import BaseCDRequirementGroupResource
from openprocurement.tender.core.procedure.models.criterion import RequirementGroup, PatchRequirementGroup
from openprocurement.tender.competitivedialogue.procedure.state.criterion_rg import CDRequirementGroupState
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from openprocurement.tender.core.procedure.validation import (
    unless_administrator,
    unless_admins,
    validate_item_owner,
    validate_input_data,
    validate_patch_data_simple
)
from openprocurement.tender.competitivedialogue.procedure.validation import unless_cd_bridge


class BaseStage2RequirementGroupResource(BaseCDRequirementGroupResource):

    @json_view(
        content_type="application/json",
        validators=(
                unless_cd_bridge(unless_admins(unless_administrator(
                    validate_item_owner("tender")
                ))),
                validate_input_data(RequirementGroup),
        ),
        permission="create_rg",
    )
    def collection_post(self) -> Optional[dict]:
        return super().collection_post()

    @json_view(
        content_type="application/json",
        validators=(
                unless_cd_bridge(unless_admins(unless_administrator(
                    validate_item_owner("tender")
                ))),
                validate_input_data(PatchRequirementGroup),
                validate_patch_data_simple(RequirementGroup, "requirement_group"),
        ),
        permission="edit_rg",
    )
    def patch(self) -> Optional[dict]:
        return super().patch()


@resource(
    name="{}:Criteria Requirement Group".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage 2 EU requirement group",
)
class Stage2EURequirementGroupResource(BaseStage2RequirementGroupResource):
    state_class = CDRequirementGroupState


@resource(
    name="{}:Criteria Requirement Group".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue Stage 2 UA requirement group",
)
class Stage2UARequirementGroupResource(BaseStage2RequirementGroupResource):
    state_class = CDRequirementGroupState
