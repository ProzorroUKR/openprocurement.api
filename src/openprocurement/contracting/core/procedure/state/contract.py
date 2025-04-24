from itertools import zip_longest
from logging import getLogger

from schematics.types import BaseType

from openprocurement.api.context import get_request
from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.procedure.utils import to_decimal
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.state.contract import ContractStateMixing
from openprocurement.tender.core.procedure.validation import validate_items_unit_amount

LOGGER = getLogger(__name__)


class BaseContractState(BaseState, ContractStateMixing):
    terminated_statuses = ("terminated",)

    def always(self, data) -> None:
        super().always(data)

    def on_patch(self, before, after) -> None:
        self.validate_contract_patch(self.request, before, after)
        if after.get("value"):
            self.synchronize_items_unit_value(after)
        super().on_patch(before, after)

    def validate_contract_patch(self, request, before: dict, after: dict):
        self.validate_patch_contract_items(request, before, after)
        self.validate_update_contracting_items_unit_value_amount(request, before, after)
        self.validate_update_contract_value_net_required(request, before, after)
        self.validate_update_contract_value_net_required(request, before, after, name="amountPaid")
        self.validate_update_contract_value(request, before, after)
        self.validate_update_contracting_value_identical(request, before, after)
        self.validate_update_contract_value_amount(request, before, after)
        self.validate_update_contract_paid_amount(request, before, after)
        self.validate_update_contract_value_net_required(request, before, after)
        self.validate_terminate_contract_without_amountPaid(request, before, after)

    def validate_patch_contract_items(self, request, before: dict, after: dict) -> None:
        # TODO: Remove this logic later with adding new endpoint for items in contract

        after_status = after["status"]
        if after_status == "active":
            item_patch_fields = (
                "description",
                "description_en",
                "description_ru",
                "unit",
                "deliveryDate",
                "deliveryAddress",
                "deliveryLocation",
                "quantity",
            )
        else:
            item_patch_fields = ("unit", "quantity")
        items_before = before.get("items", [])
        items_after = after.get("items", [])
        for item_before, item_after in zip_longest(items_before, items_after):
            if None in (item_before, item_after):
                raise_operation_error(get_request(), "Can't change items list length")
            else:
                # check deletion of fields
                if set(item_before.keys()) - set(item_after.keys()):
                    raise_operation_error(
                        get_request(),
                        f"Forbidden to delete fields {set(item_before.keys()) - set(item_after.keys())}",
                    )
                for k in item_before.keys() | item_after.keys():
                    before, after = item_before.get(k), item_after.get(k)
                    if k not in item_patch_fields and before != after:
                        raise_operation_error(
                            get_request(),
                            f"Updated could be only {item_patch_fields} in item, {k} change forbidden",
                        )
                    # check fields deletion in dict objects such as deliveryAddress, deliveryLocation, etc.
                    if isinstance(before, dict) and isinstance(after, dict) and set(before.keys()) - set(after.keys()):
                        raise_operation_error(
                            get_request(),
                            f"Forbidden to delete fields in {k}: {set(before.keys()) - set(after.keys())}",
                        )

                    if (
                        k == "unit"
                        and before is not None  # for ESCO there could be no unit for contract, but it can be added
                        and before.get("value")
                    ):
                        if before["value"]["currency"] != after["value"]["currency"]:
                            raise_operation_error(
                                get_request(),
                                "Forbidden to change currency in contract items unit",
                            )

    def validate_update_contracting_items_unit_value_amount(self, request, before, after) -> None:
        if after.get("items"):
            self._validate_contract_items_unit_value_amount(after)

    def _validate_contract_items_unit_value_amount(self, contract: dict) -> None:
        items_unit_value_amount = []
        for item in contract.get("items", ""):
            if item.get("unit") and item.get("quantity") is not None:
                if item["unit"].get("value"):
                    if item["quantity"] == 0 and item["unit"]["value"]["amount"] != 0:
                        raise_operation_error(
                            get_request(),
                            "Item.unit.value.amount should be updated to 0 if item.quantity equal to 0",
                            status=422,
                        )
                    items_unit_value_amount.append(
                        to_decimal(item["quantity"]) * to_decimal(item["unit"]["value"]["amount"])
                    )

        validate_items_unit_amount(items_unit_value_amount, contract)

    @staticmethod
    def validate_update_contracting_value_identical(request, before, after):
        value = after.get("value")
        paid_data = request.validated["json_data"].get("amountPaid")
        for attr in ("currency",):
            if value and paid_data and paid_data.get(attr) is not None:
                if value.get(attr) != paid_data.get(attr):
                    raise_operation_error(
                        request,
                        f"{attr} of amountPaid should be identical to {attr} of value of contract",
                        name="amountPaid",
                    )

    @staticmethod
    def validate_update_contract_value_net_required(request, before, after, name="value"):
        value = after.get(name)
        if value and (before.get(name) != after.get(name) or before.get("status") != after.get("status")):
            contract_amount_net = value.get("amountNet")
            if contract_amount_net is None:
                raise_operation_error(
                    request,
                    {"amountNet": BaseType.MESSAGES["required"]},
                    status=422,
                    name=name,
                )

    def validate_update_contract_paid_amount(self, request, before, after):
        value = after.get("value")
        paid = after.get("amountPaid")
        if not paid:
            return
        self.validate_update_contract_value_amount(request, before, after, name="amountPaid")
        if not value:
            return
        attr = "amountNet"
        paid_amount = paid.get(attr)
        value_amount = value.get(attr)
        if value_amount and paid_amount > value_amount:
            raise_operation_error(
                request,
                f"AmountPaid {attr} can`t be greater than value {attr}",
                name="amountPaid",
            )

    @staticmethod
    def validate_terminate_contract_without_amountPaid(request, before, after):
        if after.get("status", "active") == "terminated" and not after.get("amountPaid"):
            raise_operation_error(request, "Can't terminate contract while 'amountPaid' is not set")
