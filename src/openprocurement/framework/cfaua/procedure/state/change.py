from openprocurement.api.context import get_request, get_request_now
from openprocurement.api.procedure.state.base import BaseState
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
