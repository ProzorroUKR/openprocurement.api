# -*- coding: utf-8 -*-

from decimal import Decimal, ROUND_UP, ROUND_FLOOR

from schematics.types import BaseType
from openprocurement.api.utils import (
    update_logging_context,
    error_handler,
    raise_operation_error,
    handle_data_exceptions,
    requested_fields_changes,
)
from openprocurement.api.procedure.utils import to_decimal
from openprocurement.tender.core.constants import AMOUNT_NET_COEF
from openprocurement.tender.pricequotation.constants import PQ




def validate_update_contract_value(request, name="value", attrs=("currency",), **kwargs):
    data = request.validated["data"]
    value = data.get(name)
    if value:
        for ro_attr in attrs:
            field = getattr(request.context, name)
            if field and value.get(ro_attr) != field.to_native().get(ro_attr):
                raise_operation_error(request, "Can't update {} for contract {}".format(ro_attr, name), name=name)


def validate_update_contract_value_net_required(request, name="value", **kwargs):
    data = request.validated["data"]
    value = data.get(name)
    if value is not None and requested_fields_changes(request, (name, "status")):
        contract_amount_net = value.get("amountNet")
        if contract_amount_net is None:
            raise_operation_error(request, dict(amountNet=BaseType.MESSAGES["required"]), status=422, name=name)


def validate_update_contract_value_amount(request, name="value", **kwargs):
    data = request.validated["data"]
    contract_value = data.get(name)
    value = data.get("value") or data.get(name)
    if contract_value and requested_fields_changes(request, (name, "status")):
        amount = to_decimal(contract_value.get("amount"))
        amount_net = to_decimal(contract_value.get("amountNet"))
        tax_included = contract_value.get("valueAddedTaxIncluded")

        if not (amount == 0 and amount_net == 0):
            if tax_included:
                amount_max = (amount_net * AMOUNT_NET_COEF).quantize(Decimal("1E-2"), rounding=ROUND_UP)
                if (amount < amount_net or amount > amount_max):
                    raise_operation_error(
                        request,
                        "Amount should be equal or greater than amountNet and differ by "
                        "no more than {}%".format(AMOUNT_NET_COEF * 100 - 100),
                        name=name,
                    )
            else:
                if amount != amount_net:
                    raise_operation_error(request, "Amount and amountNet should be equal", name=name)

def validate_contract_items_unit_value_amount(request, contract, **kwargs):
    items_unit_value_amount = []
    for item in contract.items:
        if item.unit and item.quantity is not None:
            if item.unit.value:
                if item.quantity == 0 and item.unit.value.amount != 0:
                    raise_operation_error(
                        request, "Item.unit.value.amount should be updated to 0 if item.quantity equal to 0"
                    )
                items_unit_value_amount.append(
                    to_decimal(item.quantity) * to_decimal(item.unit.value.amount)
                )

    if items_unit_value_amount and contract.value:
        calculated_value = sum(items_unit_value_amount)

        if calculated_value.quantize(Decimal("1E-2"), rounding=ROUND_FLOOR) > to_decimal(contract.value.amount):
            raise_operation_error(
                request, "Total amount of unit values can't be greater than contract.value.amount"
            )


def validate_tender_matches_plan(request, **kwargs):
    plan = request.validated["plan"]
    tender = request.validated.get("tender") or request.validated.get("tender_data")

    plan_identifier = plan.procuringEntity.identifier
    tender_identifier = tender.get("procuringEntity", {}).get("identifier", {})
    if plan.tender.procurementMethodType == "centralizedProcurement" and plan_identifier.id == "01101100":
        plan_identifier = plan.buyers[0].identifier

    if plan_identifier.id != tender_identifier.get("id") or plan_identifier.scheme != tender_identifier.get("scheme"):
        request.errors.add(
            "body",
            "procuringEntity",
            "procuringEntity.identifier doesn't match: {} {} != {} {}".format(
                plan_identifier.scheme, plan_identifier.id, tender_identifier["scheme"], tender_identifier["id"]
            ),
        )

    pattern = plan.classification.id[:3] if plan.classification.id.startswith("336") else plan.classification.id[:4]
    for i, item in enumerate(tender.get("items", "")):
        # item.classification may be empty in pricequotaiton
        if item.get("classification") and item["classification"]["id"][: len(pattern)] != pattern:
            request.errors.add(
                "body",
                "items[{}].classification.id".format(i),
                "Plan classification.id {} and item's {} should be of the same group {}".format(
                    plan.classification.id, item["classification"]["id"], pattern
                ),
            )

    if request.errors:
        request.errors.status = 422
        raise error_handler(request)


def validate_tender_plan_procurement_method_type(request, **kwargs):
    plan = request.validated["plan"]
    tender = request.validated["tender_data"]
    tender_type = tender.get("procurementMethodType")

    if plan.tender.procurementMethodType not in (tender_type, "centralizedProcurement"):
        if tender_type == PQ and plan.tender.procurementMethodType == "belowThreshold":
            return
        request.errors.add(
            "body",
            "procurementMethodType",
            "procurementMethodType doesn't match: {} != {}".format(
                plan.tender.procurementMethodType, tender_type
            ),
        )
        request.errors.status = 422
        raise error_handler(request)


def validate_plan_budget_breakdown(request, **kwargs):
    plan = request.validated["plan"]

    if not plan.budget or not plan.budget.breakdown:
        request.errors.add("body", "budget.breakdown", "Plan should contain budget breakdown")
        request.errors.status = 422
        raise error_handler(request)



def validate_tender_plan_data(request, **kwargs):
    plan_id = request.validated["data"]["id"]
    update_logging_context(request, {"plan_id": plan_id})

    plan = request.extract_plan(plan_id)
    with handle_data_exceptions(request):
        plan.validate()
    request.validated["plan"] = plan
    request.validated["plan_src"] = plan.serialize("plain")
