from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.procedure.utils import parse_date
from openprocurement.api.utils import get_now, raise_operation_error
from openprocurement.contracting.contract.procedure.models.change import Change, PatchChange, PostChange
from openprocurement.contracting.core.procedure.state.change import (
    ContractChangeStateMixin,
)
from openprocurement.contracting.core.procedure.state.contract import ContractRequestRulesMixin


class ChangeState(ContractRequestRulesMixin, BaseState, ContractChangeStateMixin):
    post_data_model = PostChange
    patch_data_model = PatchChange
    data_model = Change

    # --- request validation (called from the views) ---

    def validate_change_post_request(self):
        if self.request.authenticated_role not in ("Administrator", "admins"):
            self.validate_contract_owner()
        self.validate_input_data(self.get_post_data_model())
        self.validate_change_date_signed_not_in_future()
        self.validate_contract_change_allowed()
        self.validate_contract_change_no_pending()

    def validate_change_patch_request(self):
        if self.request.authenticated_role not in ("Administrator", "admins"):
            self.validate_contract_owner()
        self.validate_patch_input_data(self.get_patch_data_model())
        self.validate_patch_data(self.get_data_model(), item_name="change")
        self.validate_change_date_signed_not_in_future()
        self.validate_contract_change_allowed()
        self.validate_contract_change_update_allowed()

    def validate_change_date_signed_not_in_future(self):
        date_signed = self.request.validated["data"].get("dateSigned")
        if date_signed and parse_date(date_signed) > get_now():
            raise_operation_error(
                self.request,
                ["Contract signature date can't be in the future"],
                status=422,
                name="dateSigned",
            )

    def change_on_post(self, data):
        self.change_always(data)

    def change_on_patch(self, before, after):
        if "status" in after and before.get("status") != after["status"]:
            self.change_status_up(before["status"], after["status"], after)
        self.change_always(after)

    def change_always(self, data):
        tender = self.request.validated["tender"]
        self.validate_change_rationale_types(data, tender)
        self.validate_change_date_signed(data)

    def change_status_up(self, before_status, after_status, data):
        self.validate_update_contract_change_status(self.request)
        data["date"] = get_now()

    def validate_change_date_signed(self, data):
        contract = self.request.validated["contract"]
        if data.get("dateSigned"):
            changes = contract.get("changes", [])
            if self.request.method == "PATCH":
                changes = changes[:-1]

            if len(changes) > 0:  # has previous changes
                last_change = changes[-1]
                last_date_signed = last_change["dateSigned"]
                if not last_date_signed:  # BBB old active changes
                    last_date_signed = last_change["date"].isoformat()
                obj_str = "last active change"
            else:
                last_date_signed = contract.get("dateSigned")
                obj_str = "contract"

            if last_date_signed:  # BBB very old contracts
                if parse_date(data["dateSigned"]) < parse_date(last_date_signed):
                    # Can't move validator because of code above
                    raise_operation_error(
                        self.request,
                        f"Change dateSigned ({data['dateSigned']}) can't be "
                        f"earlier than {obj_str} dateSigned ({last_date_signed})",
                    )

    def validate_update_contract_change_status(self, data):
        json_data = self.request.validated["data"]
        if not json_data.get("dateSigned", ""):
            raise_operation_error(
                self.request,
                "Can't update contract change status. 'dateSigned' is required.",
            )
