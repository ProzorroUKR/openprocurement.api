from openprocurement.api.procedure.serializers.base import BaseSerializer
from openprocurement.api.procedure.utils import get_items, set_item
from openprocurement.api.procedure.validation import (
    unless_administrator,
    unless_admins,
    validate_input_data,
    validate_patch_data,
)
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.contracting.core.procedure.models.change import (
    Change,
    PatchChange,
    PostChange,
)
from openprocurement.contracting.core.procedure.state.change import ChangeState
from openprocurement.contracting.core.procedure.utils import save_contract
from openprocurement.contracting.core.procedure.validation import (
    validate_contract_change_action_not_in_allowed_contract_status,
    validate_contract_change_update_not_in_allowed_change_status,
    validate_contract_owner,
    validate_create_contract_change,
)
from openprocurement.contracting.core.procedure.views.base import ContractBaseResource


def resolve_change(request):
    match_dict = request.matchdict
    if match_dict.get("change_id"):
        change_id = match_dict["change_id"]
        contract = request.validated["contract"]
        change = get_items(request, contract, "changes", change_id)
        request.validated["change"] = change[0]


class ContractsChangesResource(ContractBaseResource):
    """Contract changes resource"""

    serializer_class = BaseSerializer
    state_class = ChangeState

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_change(request)

    @json_view(permission="view_contract")
    def collection_get(self):
        """Return Contract Changes list"""
        return {"data": [self.serializer_class(i).data for i in self.request.validated["contract"].get("changes", "")]}

    @json_view(permission="view_contract")
    def get(self):
        """Return Contract Change"""
        return {"data": self.serializer_class(self.request.validated["change"]).data}

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
        """Contract Change create"""
        contract = self.request.validated["contract"]

        change = self.request.validated["data"]

        if not contract.get("changes"):
            contract["changes"] = []

        self.state.change_on_post(change)

        contract["changes"].append(change)

        if save_contract(self.request):
            self.LOGGER.info(
                f"Created change {change['id']} of contract {contract['_id']}",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "contract_change_create"},
                    {"change_id": change["id"], "contract_id": contract["_id"]},
                ),
            )
            self.request.response.status = 201
            return {"data": self.serializer_class(change).data}

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
