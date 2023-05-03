from openprocurement.tender.core.procedure.context import get_request
from openprocurement.api.context import get_now
from openprocurement.tender.belowthreshold.utils import prepare_tender_item_for_contract
from collections import defaultdict
from copy import deepcopy


def add_contracts(request, award, contract_model):
    tender = request.validated["tender"]

    # split items by relatedBuyer
    items_by_buyer = defaultdict(list)
    for item in tender["items"]:
        if item.get("relatedLot") == award.get("lotID"):  # None == None in case of non-lots
            buyer_id = item.get("relatedBuyer")  # can be None
            prepared_item = prepare_tender_item_for_contract(item)
            items_by_buyer[buyer_id].append(prepared_item)

    multi_contracts = tender.get("buyers") and all(item.get("relatedBuyer") for item in tender.get("items", ""))
    value = generate_contract_value(award, multi_contracts=multi_contracts)

    # prepare contract for every buyer
    if multi_contracts:
        for buyer_id, items in items_by_buyer.items():
            add_contract_to_tender(
                contract_model, tender, items, value, buyer_id, award,
            )
    else:  # ignoring "buyer_id", even if not None
        contract_items = []
        for _, items in items_by_buyer.items():
            contract_items.extend(items)
        add_contract_to_tender(
            contract_model, tender, contract_items, value, None, award,
        )


def generate_contract_value(award, multi_contracts=False):
    if award.get("value"):
        value = deepcopy(award["value"])
        if multi_contracts:
            value["amountNet"], value["amount"] = 0, 0
        else:
            value["amountNet"] = value["amount"]
        return value
    return None


def add_contract_to_tender(contract_model, tender, contract_items, contract_value, buyer_id, award):
    server_id = get_request().registry.server_id
    contract_number = len(tender.get('contracts', '')) + 1
    if "contracts" not in tender:
        tender["contracts"] = []

    contract = contract_model(
        {
            "buyerID": buyer_id,
            "awardID": award["id"],
            "suppliers": award["suppliers"],
            "value": contract_value,
            "date": get_now(),
            "items": contract_items,
            "contractID": f"{tender['tenderID']}-{server_id}{contract_number}",
        }
    )
    tender["contracts"].append(
        contract.serialize()
    )
