from openprocurement.api.context import get_request, get_request_now
from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.procedure.validation import (
    validate_input_data_from_resolved_model,
    validate_patch_input_data_from_resolved_model,
)
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import validate_json_data
from openprocurement.framework.cfaua.procedure.models.change import (
    ChangeItemPriceVariation,
    ChangePartyWithdrawal,
    ChangeTaxRate,
    ChangeThirdParty,
    PatchChangeItemPriceVariation,
    PatchChangePartyWithdrawal,
    PatchChangeTaxRate,
    PatchChangeThirdParty,
    PostChangeItemPriceVariation,
    PostChangePartyWithdrawal,
    PostChangeTaxRate,
    PostChangeThirdParty,
)
from openprocurement.tender.core.procedure.utils import dt_from_iso


class ChangeState(BaseState):
    # --- request validation (called from the views) ---

    def validate_change_post_request(self):
        if self.request.authenticated_role != "Administrator":
            self.validate_item_owner("agreement")
        validate_input_data_from_resolved_model()(self.request)
        self.validate_change_date_signed_not_in_future()
        self.validate_change_agreement_status()
        self.validate_change_no_pending()

    def validate_change_patch_request(self):
        if self.request.authenticated_role != "Administrator":
            self.validate_item_owner("agreement")
        validate_patch_input_data_from_resolved_model()(self.request)
        self.validate_change_date_signed_not_in_future()
        self.validate_patch_data(self.get_parent_patch_data_model(), item_name="change")
        self.validate_change_update_allowed()

    def validate_change_date_signed_not_in_future(self):
        date_signed = self.request.validated["data"].get("dateSigned")
        if date_signed and dt_from_iso(date_signed) > get_request_now():
            raise_operation_error(
                self.request,
                ["Agreement signature date can't be in the future"],
                status=422,
                name="dateSigned",
            )

    def validate_change_agreement_status(self):
        status = self.request.validated["agreement"]["status"]
        if status != "active":
            raise_operation_error(self.request, f"Can't add agreement change in current ({status}) agreement status")

    def validate_change_no_pending(self):
        changes = self.request.validated["agreement"].get("changes")
        if changes and changes[-1]["status"] == "pending":
            raise_operation_error(self.request, "Can't create new agreement change while any (pending) change exists")

    def validate_change_update_allowed(self):
        status = self.request.validated["change"]["status"]
        if status in ("active", "cancelled"):
            raise_operation_error(self.request, f"Can't update agreement change in current ({status}) status")

    def get_post_data_model(self):
        request = get_request()
        data = validate_json_data(request)
        if "rationaleType" not in data:
            raise_operation_error(get_request(), "Can't add change without rationaleType")
        if data["rationaleType"] == "taxRate":
            return PostChangeTaxRate
        elif data["rationaleType"] == "itemPriceVariation":
            return PostChangeItemPriceVariation
        elif data["rationaleType"] == "thirdParty":
            return PostChangeThirdParty
        elif data["rationaleType"] == "partyWithdrawal":
            return PostChangePartyWithdrawal
        raise_operation_error(
            get_request(),
            "rationaleType should be one of {}".format(
                ["taxRate", "itemPriceVariation", "thirdParty", "partyWithdrawal"]
            ),
        )

    def get_patch_data_model(self):
        request = get_request()
        data = request.validated["change"]
        if data["rationaleType"] == "taxRate":
            return PatchChangeTaxRate
        elif data["rationaleType"] == "itemPriceVariation":
            return PatchChangeItemPriceVariation
        elif data["rationaleType"] == "thirdParty":
            return PatchChangeThirdParty
        return PatchChangePartyWithdrawal

    def get_parent_patch_data_model(self):
        request = get_request()
        data = request.validated["change"]
        if data["rationaleType"] == "taxRate":
            return ChangeTaxRate
        elif data["rationaleType"] == "itemPriceVariation":
            return ChangeItemPriceVariation
        elif data["rationaleType"] == "thirdParty":
            return ChangeThirdParty
        return ChangePartyWithdrawal

    def on_post(self, data):
        self.validate_change_date_signed(data)
        super().on_post(data)

    def pre_patch(self, before, after):
        if "status" in after and after["status"] != before["status"]:  # status change
            self.validate_update_agreement_change_status(after)
            after["date"] = get_request_now().isoformat()

    def on_patch(self, before, after):
        self.validate_change_date_signed(after)
        super().on_patch(before, after)

    def validate_change_date_signed(self, change):
        if change.get("dateSigned"):
            agreement = get_request().validated["agreement_src"]
            changes = agreement.get("changes", [])
            active_changes = [agreem_change for agreem_change in changes if agreem_change["status"] == "active"]
            if len(active_changes) > 0:
                last_change = active_changes[-1]
                last_date_signed = last_change.get("dateSigned")
                if not last_date_signed:  # BBB old active changes
                    last_date_signed = last_change.get("date")
                obj_str = "last active change"
            else:
                last_date_signed = agreement.get("dateSigned")
                obj_str = "agreement"

            if last_date_signed:  # BBB very old agreements
                if dt_from_iso(change["dateSigned"]) < dt_from_iso(last_date_signed):
                    raise_operation_error(
                        get_request(),
                        f"Change dateSigned ({change['dateSigned']}) can't be earlier "
                        f"than {obj_str} dateSigned ({last_date_signed})",
                    )

    def validate_update_agreement_change_status(self, data):
        if data["status"] == "active" and not data.get("dateSigned", ""):
            raise_operation_error(
                get_request(),
                "Can't update agreement change status. 'dateSigned' is required.",
            )
