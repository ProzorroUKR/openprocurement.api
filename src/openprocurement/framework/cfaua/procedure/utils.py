from openprocurement.api.utils import raise_operation_error
from openprocurement.framework.cfaua.constants import CFA_UA, MIN_BIDS_NUMBER


def get_active_contracts_count(agreement):
    return len([contract for contract in agreement.get("contracts") if contract["status"] == "active"])


def apply_modifications(request, agreement):
    warnings = []
    if not agreement["changes"][-1].get("modifications"):
        return
    for modification in agreement["changes"][-1]["modifications"]:
        if agreement["changes"][-1]["rationaleType"] != "partyWithdrawal":
            unit_prices = [
                unit_price
                for contract in agreement.get("contracts", [])
                for unit_price in contract.get("unitPrices", [])
                if unit_price["relatedItem"] == modification["itemId"]
            ]

            for unit_price in unit_prices:
                if modification.get("addend"):
                    unit_price["value"]["amount"] += modification["addend"]
                if modification.get("factor") is not None:
                    unit_price["value"]["amount"] *= modification["factor"]
                if unit_price["value"]["amount"] <= 0:
                    raise_operation_error(request, "unitPrice:value:amount can't be equal or less than 0.")
                unit_price["value"]["amount"] = round(unit_price["value"]["amount"], 2)
        else:
            for contract in agreement.get("contracts"):
                if contract["id"] == modification["contractId"]:
                    contract["status"] = "unsuccessful"
                    break
    if get_active_contracts_count(agreement) < MIN_BIDS_NUMBER:
        warnings.append(f"Min active contracts in FrameworkAgreement less than {MIN_BIDS_NUMBER}.")
    return warnings


def convert_agreement_type(agreement_type):
    if agreement_type == "cfaua":
        return CFA_UA
    return agreement_type
