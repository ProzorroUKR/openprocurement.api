# -*- coding: utf-8 -*-
from decimal import Decimal, ROUND_FLOOR

from openprocurement.api.utils import (
    raise_operation_error,
    to_decimal,
)
from openprocurement.api.validation import (
    _validate_accreditation_level,
    OPERATIONS,
)
from openprocurement.tender.core.procedure.validation import (
    validate_update_contract_value,
    validate_update_contract_value_amount,
    validate_update_contract_value_net_required,
)
from openprocurement.contracting.core.utils import get_transaction_by_id
from openprocurement.contracting.core.procedure.utils import is_tender_owner, is_contract_owner, is_bid_owner


def _validate_contract_accreditation_level(request, model):
    _validate_accreditation_level(request, model.create_accreditations, "contract", "creation")


# changes
def validate_contract_change_add_not_in_allowed_contract_status(request, **kwargs):
    contract = request.validated["contract"]
    if contract["status"] not in ["pending", "active"]:
        raise_operation_error(
            request, f"Can't add contract change in current ({contract['status']}) contract status"
        )


def validate_create_contract_change(request, **kwargs):
    contract = request.validated["contract"]
    if contract.get("changes") and contract["changes"][-1]["status"] == "pending":
        raise_operation_error(request, "Can't create new contract change while any (pending) change exists")


def validate_contract_change_update_not_in_allowed_change_status(request, **kwargs):
    change = request.validated["change"]
    if change["status"] == "active":
        raise_operation_error(request, f"Can't update contract change in current ({change['status']}) status")


# contract
def validate_contract_update_not_in_allowed_status(request, **_):
    contract = request.validated["contract"]
    if contract["status"] not in ["pending", "active"]:
        raise_operation_error(request, f"Can't update contract in current ({contract['status']}) status")


def validate_terminate_contract_without_amountPaid(request, **_):
    contract = request.validated["data"]
    if contract.get("status", "active") == "terminated" and not contract.get("amountPaid"):
        raise_operation_error(request, "Can't terminate contract while 'amountPaid' is not set")


def validate_credentials_generate(request, **_):
    contract = request.validated["contract"]
    if contract["status"] not in ["pending", "active"]:
        raise_operation_error(
            request, f"Can't generate credentials in current ({contract['status']}) contract status"
        )


# contract document
def validate_contract_document_operation_not_in_allowed_contract_status(request, **_):
    if request.validated["contract"]["status"] not in ["pending", "active"]:
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document in current "
            f"({request.validated['contract']['status']}) contract status"
        )


def validate_transaction_existence(request, **kwargs):
    transaction = get_transaction_by_id(request)
    if not transaction:
        raise_operation_error(request, "Transaction does not exist", status=404)


def validate_contract_items_unit_value_amount(request, contract, **_):
    items_unit_value_amount = []
    for item in contract.get("items", ""):
        if item.get("unit") and item.get("quantity") is not None:
            if item["unit"].get("value"):
                if item["quantity"] == 0 and item["unit"]["value"]["amount"] != 0:
                    raise_operation_error(
                        request, "Item.unit.value.amount should be updated to 0 if item.quantity equal to 0"
                    )
                items_unit_value_amount.append(
                    to_decimal(item["quantity"]) * to_decimal(item["unit"]["value"]["amount"])
                )

    if items_unit_value_amount and contract.get("value"):
        calculated_value = sum(items_unit_value_amount)

        if calculated_value.quantize(Decimal("1E-2"), rounding=ROUND_FLOOR) > to_decimal(contract["value"]["amount"]):
            raise_operation_error(
                request, "Total amount of unit values can't be greater than contract.value.amount"
            )


def validate_update_contracting_items_unit_value_amount(request, **_):
    contract = request.validated["data"]
    if contract.get("items"):
        validate_contract_items_unit_value_amount(request, contract)


def validate_add_document_to_active_change(request, **_):
    data = request.validated["data"]
    if "relatedItem" in data and data.get("documentOf") == "change":
        changes = request.validated["contract"].get("changes", "")
        if not any(c["id"] == data["relatedItem"] and c["status"] == "pending" for c in changes):
            raise_operation_error(request, "Can't add document to 'active' change")


# contract value and paid
def validate_update_contracting_value_amount(request, name="value", **kwargs):
    validate_update_contract_value_amount(request, name=name)


def validate_update_contracting_paid_amount(request, **kwargs):
    data = request.validated["data"]
    value = data.get("value")
    paid = data.get("amountPaid")
    if not paid:
        return
    validate_update_contracting_value_amount(request, name="amountPaid")
    if not value:
        return
    attr = "amountNet"
    paid_amount = paid.get(attr)
    value_amount = value.get(attr)
    if value_amount and paid_amount > value_amount:
        raise_operation_error(
            request,
            "AmountPaid {} can`t be greater than value {}".format(attr, attr),
            name="amountPaid",
        )


def validate_contract_patch_items_amount_unchanged(request, **_):
    if "items" not in request.validated["data"]:
        return
    old_contract_items = request.contract.get("items") or []
    new_contract_items = request.validated["data"].get("items") or []
    if len(old_contract_items) != len(new_contract_items):
        raise_operation_error(
            request, f"Can't add or remove items."
        )


def validate_update_contracting_value_readonly(request, **_):
    validate_update_contract_value(request, name="value", attrs=("currency",))


def validate_update_contracting_value_identical(request, **_):
    if "amountPaid" in request.validated["json_data"]:
        value = request.validated["data"].get("value")
        paid_data = request.validated["json_data"].get("amountPaid")
        for attr in ("currency",):
            if value and paid_data and paid_data.get(attr) is not None:
                if value.get(attr) != paid_data.get(attr):
                    raise_operation_error(
                        request,
                        f"{attr} of amountPaid should be identical to {attr} of value of contract",
                        name="amountPaid",
                    )


def validate_update_contract_paid_net_required(request, **kwargs):
    validate_update_contract_value_net_required(request, name="amountPaid")


def validate_tender_owner(request, **_):
    contract = request.validated["contract"]
    if not is_tender_owner(request, contract):
        raise_operation_error(
            request,
            "Forbidden",
            location="url",
            name="permission"
        )


def validate_contract_owner(request, **_):
    contract = request.validated["contract"]
    if not is_contract_owner(request, contract):
        raise_operation_error(
            request,
            "Forbidden",
            location="url",
            name="permission"
        )


def validate_contract_supplier(request, **_):
    contract = request.validated["contract"]
    if not is_bid_owner(request, contract):
        raise_operation_error(
            request,
            "Forbidden",
            location="url",
            name="permission"
        )


def validate_contract_participant(request, **_):
    contract = request.validated["contract"]

    if (
        not is_contract_owner(request, contract)
        and not is_bid_owner(request, contract)
    ):
        raise_operation_error(
            request,
            "Forbidden",
            location="url",
            name="permission"
        )