from typing import Optional

from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    unless_administrator,
    validate_input_data,
    validate_item_owner,
    validate_patch_data_simple,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.models.criterion import (
    PatchRequirement,
    PutRequirement,
    Requirement,
)
from openprocurement.tender.core.procedure.views.criterion_rg_requirement import (
    BaseRequirementResource,
)
from openprocurement.tender.requestforproposal.procedure.state.criterion_rg_requirement import (
    RequestForProposalRequirementState,
)


@resource(
    name="requestForProposal:Requirement Group Requirement",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
    procurementMethodType="requestForProposal",
    description="Tender requirement group requirement",
)
class RequirementResource(BaseRequirementResource):
    state_class = RequestForProposalRequirementState

    @json_view(
        content_type="application/json",
        validators=(
            unless_administrator(validate_item_owner("tender")),
            validate_input_data(PatchRequirement, none_means_remove=True),
            validate_patch_data_simple(Requirement, "requirement"),
        ),
        permission="edit_requirement",
    )
    def patch(self) -> Optional[dict]:
        return super().patch()

    @json_view(
        content_type="application/json",
        validators=(
            unless_administrator(validate_item_owner("tender")),
            validate_input_data(PutRequirement, none_means_remove=True),
            validate_patch_data_simple(Requirement, "requirement"),
        ),
        permission="edit_requirement",
    )
    def put(self):
        return super().put()
