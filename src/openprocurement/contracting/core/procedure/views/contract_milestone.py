from openprocurement.api.procedure.serializers.base import BaseSerializer
from openprocurement.api.procedure.utils import get_items, set_item
from openprocurement.api.procedure.validation import (
    unless_administrator,
    unless_admins,
    validate_input_data,
    validate_patch_data,
)
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.contracting.core.procedure.models.milestone import (
    ContractMilestone,
    PatchContractMilestone,
)
from openprocurement.contracting.core.procedure.state.milestone import (
    ContractMilestoneState,
)
from openprocurement.contracting.core.procedure.utils import save_contract
from openprocurement.contracting.core.procedure.validation import (
    validate_contract_participant,
    validate_milestone_update_in_not_allowed_status,
)
from openprocurement.contracting.core.procedure.views.base import ContractBaseResource


def resolve_milestone(request):
    match_dict = request.matchdict
    milestone_id = match_dict.get("milestone_id")
    if milestone_id:
        milestones = get_items(request, request.validated["contract"], "milestones", milestone_id)
        request.validated["milestone"] = milestones[0]


class ContractMilestoneResource(ContractBaseResource):
    state_class = ContractMilestoneState
    serializer_class = BaseSerializer

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_milestone(request)

    @json_view(permission="view_contract")
    def collection_get(self):
        contract = self.request.validated["contract"]
        data = tuple(self.serializer_class(milestone).data for milestone in contract.get("milestones", []))
        return {"data": data}

    @json_view(permission="view_contract")
    def get(self):
        return {"data": self.serializer_class(self.request.validated["milestone"]).data}

    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
            unless_admins(unless_administrator(validate_contract_participant)),
            validate_input_data(PatchContractMilestone),
            validate_patch_data(ContractMilestone, item_name="milestone"),
            unless_admins(unless_administrator(validate_milestone_update_in_not_allowed_status)),
        ),
    )
    def patch(self):
        updated = self.request.validated["data"]
        milestone = self.request.validated["milestone"]
        self.state.on_patch(milestone, updated)
        set_item(
            self.request.validated["contract"],
            "milestones",
            milestone["id"],
            updated,
        )
        if save_contract(self.request):
            self.LOGGER.info(
                f"Updated contract milestone {self.request.validated['milestone']['id']}",
                extra=context_unpack(self.request, {"MESSAGE_ID": "contract_milestone_patch"}),
            )
            return {"data": self.serializer_class(updated).data}
