from cornice.resource import resource

from openprocurement.api.procedure.utils import set_item
from openprocurement.api.procedure.validation import (
    unless_administrator,
    unless_admins,
    validate_input_data,
    validate_patch_data,
)
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.contracting.contract.procedure.models.change import (
    Change,
    PatchChange,
    PostChange,
)
from openprocurement.contracting.contract.procedure.state.change import ChangeState
from openprocurement.contracting.core.procedure.utils import save_contract
from openprocurement.contracting.core.procedure.validation import (
    validate_contract_change_action_not_in_allowed_contract_status,
    validate_contract_change_update_not_in_allowed_change_status,
    validate_contract_owner,
    validate_create_contract_change,
)
from openprocurement.contracting.core.procedure.views.change import (
    ContractsChangesResource as BaseContractsChangesResource,
)


@resource(
    name="Contract changes",
    collection_path="/contracts/{contract_id}/changes",
    path="/contracts/{contract_id}/changes/{change_id}",
    contractType="contract",
    description="Contracts Changes",
)
class ContractsChangesResource(BaseContractsChangesResource):
    state_class = ChangeState

    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
            unless_administrator(unless_admins(validate_contract_owner)),
            validate_input_data(PostChange),
            validate_contract_change_action_not_in_allowed_contract_status,
            validate_create_contract_change,
        ),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        permission="edit_contract",
        validators=(
            unless_administrator(unless_admins(validate_contract_owner)),
            validate_input_data(PatchChange, none_means_remove=True),
            validate_patch_data(Change, item_name="change"),
            validate_contract_change_action_not_in_allowed_contract_status,
            validate_contract_change_update_not_in_allowed_change_status,
        ),
    )
    def patch(self):
        """Contract change edit"""

        updated = self.request.validated["data"]
        if updated:
            change = self.request.validated["change"]
            self.state.change_on_patch(change, updated)
            set_item(self.request.validated["contract"], "changes", change["id"], updated)
            if save_contract(self.request):
                self.LOGGER.info(
                    f"Updated contract change {change['id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "contract_change_patch"}),
                )
                return {"data": self.serializer_class(updated).data}
