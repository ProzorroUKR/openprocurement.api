from openprocurement.api.procedure.utils import parse_date
from openprocurement.api.utils import get_now, raise_operation_error
from openprocurement.contracting.core.procedure.state.contract import BaseContractState


class ChangeState(BaseContractState):
    def change_on_post(self, data):
        self.change_always(data)

    def change_on_patch(self, before, after):
        if "status" in after and before.get("status") != after["status"]:
            self.change_status_up(before["status"], after["status"], after)
        self.change_always(after)

    def change_always(self, data):
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
