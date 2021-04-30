from openprocurement.api.validation import OPERATIONS
from openprocurement.api.constants import GUARANTEE_ALLOWED_TENDER_TYPES
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.cfaselectionua.procedure.utils import equals_decimal_and_corrupted
from decimal import Decimal


def get_supplier_contract(contracts, tenderers):
    for contract in contracts:
        if contract["status"] == "active":
            for supplier in contract.get("suppliers", ""):
                for tenderer in tenderers:
                    if supplier["identifier"]["id"] == tenderer["identifier"]["id"]:
                        return contract


def validate_bid_vs_agreement(request, **_):
    data = request.validated["data"]
    if data:
        tender = get_tender()
        supplier_contract = get_supplier_contract(tender["agreements"][0]["contracts"], data["tenderers"])

        if not supplier_contract:
            raise_operation_error(request, "Bid is not a member of agreement")

        if (
            data.get("lotValues")
            and supplier_contract.get("value")
            and Decimal(data["lotValues"][0]["value"]["amount"]) > Decimal(supplier_contract["value"]["amount"])
        ):
            raise_operation_error(request, "Bid value.amount can't be greater than contact value.amount.")

        contract_parameters = {p["code"]: p["value"] for p in supplier_contract.get("parameters", "")}
        for p in data.get("parameters", ""):
            code = p["code"]
            if (
                code not in contract_parameters
                or not equals_decimal_and_corrupted(Decimal(p["value"]), contract_parameters[code])
            ):
                raise_operation_error(request, "Can't post inconsistent bid")


def validate_bid_document_operation_with_not_pending_award(request, **_):
    tender = request.validated["tender"]
    bid_id = request.validated["bid"]["id"]
    if tender["status"] == "active.qualification" and not any(
        award["bid_id"] == bid_id and award["status"] == "pending"
        for award in tender.get("awards", "")
    ):
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document because award of bid is not in pending state",
        )


def validate_bid_document_operation_in_not_allowed_tender_status(request, **_):
    tender = request.validated["tender"]
    if tender["status"] == "active.awarded" and tender["procurementMethodType"] in GUARANTEE_ALLOWED_TENDER_TYPES:
        bid_id = request.validated["bid"]["id"]
        data_list = request.validated["data"]
        if not isinstance(data_list, list):
            data_list = [data_list]

        for data in data_list:
            if (
                data.get("documentType", "") == "contractGuarantees"
                and any(award["status"] == "active" and award["bid_id"] == bid_id
                        for award in tender.get("awards", ""))
                and any(
                    criterion["classification"]["id"] == "CRITERION.OTHER.CONTRACT.GUARANTEE"
                    for criterion in tender.get("criteria", "")
                )
            ):
                pass  # contractGuarantees documents are allowed if award for this bid is active
            else:
                raise_operation_error(
                    request,
                    f"Can't {OPERATIONS.get(request.method)} document "
                    f"in current ({tender['status']}) tender status"
                )
    elif tender["status"] not in ("active.tendering", "active.qualification"):
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document "
            f"in current ({tender['status']}) tender status"
        )
