from typing import Optional

from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    unless_administrator,
    unless_admins,
    validate_input_data,
    validate_input_data_from_resolved_model,
    validate_item_owner,
    validate_patch_data_simple,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.competitivedialogue.procedure.state.criterion_rg_requirement import (
    CDRequirementState,
)
from openprocurement.tender.core.procedure.models.criterion import (
    PostRequirement,
    Requirement,
)
from openprocurement.tender.core.procedure.views.criterion_rg_requirement import (
    BaseRequirementResource,
)


class BaseStage2RequirementResource(BaseRequirementResource):
    @json_view(
        content_type="application/json",
        validators=(
            unless_admins(unless_administrator(validate_item_owner("tender"))),
            validate_input_data(PostRequirement),
        ),
        permission="create_requirement",
    )
    def collection_post(self) -> Optional[dict]:
        return super().collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            unless_admins(unless_administrator(validate_item_owner("tender"))),
            validate_input_data_from_resolved_model(),
            validate_patch_data_simple(Requirement, "requirement"),
        ),
        permission="edit_requirement",
    )
    def patch(self) -> Optional[dict]:
        return super().patch()

    @json_view(
        content_type="application/json",
        validators=(
            unless_admins(unless_administrator(validate_item_owner("tender"))),
            validate_input_data_from_resolved_model(none_means_remove=True),
            validate_patch_data_simple(Requirement, "requirement"),
        ),
        permission="edit_requirement",
    )
    def put(self) -> Optional[dict]:
        return super().put()


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
    state_class = CDRequirementState


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
    state_class = CDRequirementState
