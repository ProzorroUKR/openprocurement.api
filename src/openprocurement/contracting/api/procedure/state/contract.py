from logging import getLogger
from itertools import zip_longest
from decimal import Decimal, ROUND_FLOOR

from openprocurement.api.context import get_request
from openprocurement.tender.core.procedure.state.base import BaseState
from openprocurement.tender.core.procedure.state.contract import ContractStateMixing
from openprocurement.api.utils import raise_operation_error, to_decimal

LOGGER = getLogger(__name__)


class ContractState(BaseState, ContractStateMixing):
    terminated_statuses = ("terminated",)

    def always(self, data) -> None:
        super().always(data)

    def on_patch(self, before, after) -> None:
        self.validate_patch_contract_items(before, after)
        self.validate_update_contracting_items_unit_value_amount()
        if after.get("value"):
            self.synchronize_items_unit_value(after)
        super().on_patch(before, after)

    def validate_patch_contract_items(self, before: dict, after: dict) -> None:
        # TODO: Remove this logic later with adding new endpoint for items in contract
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
        items_before = before.get("items", [])
        items_after = after.get("items", [])
        for item_before, item_after in zip_longest(items_before, items_after):
            if None in (item_before, item_after):
                raise_operation_error(
                    get_request(),
                    "Can't change items list length"
                )
            else:
                for k in item_before.keys() | item_after.keys():
                    before, after = item_before.get(k), item_after.get(k)
                    if not before and not after:  # [] or None check
                        continue

                    if k not in item_patch_fields and before != after:
                        raise_operation_error(
                            get_request(),
                            f"Updated could be only {item_patch_fields} in item"
                        )

    def validate_update_contracting_items_unit_value_amount(self) -> None:
        request = get_request()
        contract = request.validated["data"]
        if contract.get("items"):
            self._validate_contract_items_unit_value_amount(contract)

    def _validate_contract_items_unit_value_amount(self, contract: dict) -> None:
        items_unit_value_amount = []
        for item in contract.get("items", ""):
            if item.get("unit") and item.get("quantity") is not None:
                if item["unit"].get("value"):
                    if item["quantity"] == 0 and item["unit"]["value"]["amount"] != 0:
                        raise_operation_error(
                            get_request(), "Item.unit.value.amount should be updated to 0 if item.quantity equal to 0"
                        )
                    items_unit_value_amount.append(
                        to_decimal(item["quantity"]) * to_decimal(item["unit"]["value"]["amount"])
                    )

        if items_unit_value_amount and contract.get("value"):
            calculated_value = sum(items_unit_value_amount)

            if calculated_value.quantize(Decimal("1E-2"), rounding=ROUND_FLOOR) > to_decimal(
                    contract["value"]["amount"]):
                raise_operation_error(
                    get_request(), "Total amount of unit values can't be greater than contract.value.amount"
                )
