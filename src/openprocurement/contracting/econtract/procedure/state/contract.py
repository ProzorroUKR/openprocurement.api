from uuid import uuid4

from openprocurement.api.context import get_request, get_request_now
from openprocurement.api.utils import raise_operation_error
from openprocurement.contracting.core.procedure.models.access import AccessRole
from openprocurement.contracting.core.procedure.state.contract import (
    ContractState as BaseContractState,
)
from openprocurement.tender.core.procedure.contracting import (
    upload_contract_pdf_document,
)


class EContractState(BaseContractState):
    def on_patch(self, before, after) -> None:
        if after["status"] == "pending" and any(
            doc.get("documentType") == "contractSignature" for doc in before.get("documents", [])
        ):
            raise_operation_error(
                self.request,
                f"Forbidden to patch already signed contract in status {after['status']}",
            )
        super().on_patch(before, after)

    def status_up(self, before: str, after: str, data: dict) -> None:
        super().status_up(before, after, data)
        if before != "active" and after == "active":
            self.validate_required_all_participants_signatures(data)

    def validate_required_all_participants_signatures(self, data: dict) -> None:
        suppliers_count = len(data.get("suppliers", []))
        participants_count = suppliers_count + 1  # all suppliers + buyer signature
        signs_count = len([doc for doc in data.get("documents", []) if doc.get("documentType") == "contractSignature"])
        if signs_count != participants_count:
            raise_operation_error(
                self.request,
                f"contractSignature document type for all participants "
                f"is required for contract in `{data.get('status')}` status",
                status=422,
            )

    def prepare_contract(self, before, after):
        if before is None:
            raise_operation_error(
                self.request,
                "Previous version of pending contract with cancellations not found",
            )
        for field_name in ("owner", "transfer_token", "access"):
            after[field_name] = before.get(field_name)
        self.set_author_of_object(after)

    def validate_on_post(self, before, after) -> None:
        self.prepare_contract(before, after)
        self.validate_cancellation_reason_type(before)
        self.validate_econtract(after)
        self.validate_contract_changes(before, after)
        tender = get_request().validated["tender"]
        award = [award for award in tender.get("awards", []) if award.get("id") == after.get("awardID")][0]
        self.request.validated["award"] = award
        self.validate_dateSigned(self.request, tender, before, after)
        self.validate_patch_contract_items(self.request, before, after)
        self.validate_update_contract_value(self.request, before, after)
        self.validate_update_contract_value_net_required(self.request, before, after)
        self.validate_update_contract_value_amount(self.request, before, after)
        self.validate_contract_pending_patch(self.request, before, after)

    def validate_cancellation_reason_type(self, prev_contract):
        for cancellation in prev_contract.get("cancellations", []):
            if cancellation.get("status") == "pending" and cancellation.get("reasonType") == "signingRefusal":
                raise_operation_error(
                    self.request,
                    "For contract with cancellation reason `signingRefusal` buyer should cancel the award.",
                )

    def validate_econtract(self, after):
        for access_details in after["access"]:
            if access_details["role"] in (AccessRole.SUPPLIER, AccessRole.BUYER):
                break
        else:
            raise_operation_error(
                self.request,
                "Forbidden to POST non-electronic contract",
            )

    def validate_contract_changes(self, before, after):
        # check if there are any changes
        updated_contract_data = {}
        for f, v in after.items():
            private_fields = (
                "id",
                "transfer_token",
                "author",
                "documents",
            )
            if f not in private_fields and before.get(f) != v:
                updated_contract_data[f] = v
        item_patch_fields = [
            "items",
            "value",
            "period",
            "title",
            "title_en",
            "description",
            "description_en",
            "dateSigned",
        ]
        if after["author"] == "buyer":
            item_patch_fields.append("buyer")
        else:
            item_patch_fields.append("suppliers")
        for field_name in updated_contract_data.keys():
            if field_name not in item_patch_fields and before.get(field_name) != after.get(field_name):
                raise_operation_error(
                    get_request(),
                    f"Updated could be only {tuple(item_patch_fields)} in contract, {field_name} change forbidden",
                    status=422,
                )
            if field_name in ("suppliers", "buyers"):
                participant_obj = after.get(field_name, {})
                prev_participant_obj = before.get(field_name, {})
                if field_name == "suppliers":
                    participant_obj = after.get(field_name, [{}])[0]
                    prev_participant_obj = before.get(field_name, [{}])[0]
                for nested_field_name, value in participant_obj.items():
                    if prev_participant_obj.get(nested_field_name) != value and nested_field_name != "signerInfo":
                        raise_operation_error(
                            get_request(),
                            f"Updated could be only signerInfo in {field_name}, {nested_field_name} change forbidden",
                            status=422,
                        )

    def on_post(self, before, after):
        tender = get_request().validated["tender"]
        server_id = get_request().registry.server_id
        contract_number = len(tender.get("contracts", "")) + 1
        after.update(
            {
                "id": uuid4().hex,
                "date": get_request_now().isoformat(),
                "contractID": f"{tender['tenderID']}-{server_id}{contract_number}",
            }
        )
        upload_contract_pdf_document(self.request, after)
        self.set_object_status(before, "cancelled")
        self.set_object_status(before["cancellations"][0], "active", update_date=False)
        base_contract_data = {}
        base_contract_fields = ("id", "status", "awardID", "date", "contractID", "value")
        for field in base_contract_fields:
            base_contract_data[field] = after.get(field)
        tender["contracts"].append(base_contract_data)
        contract_changed = self.synchronize_contracts_data(before)
        self.request.validated["contract_was_changed"] = contract_changed
