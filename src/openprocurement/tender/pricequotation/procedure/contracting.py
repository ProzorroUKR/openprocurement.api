from hashlib import sha512

from openprocurement.tender.core.procedure.context import get_request, get_tender, get_award
from openprocurement.api.context import get_now
from openprocurement.tender.belowthreshold.utils import prepare_tender_item_for_contract
from openprocurement.contracting.econtract.procedure.models.contract import PostContract
from openprocurement.contracting.core.procedure.utils import save_contract
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

    contracts_added = []
    # prepare contract for every buyer
    if multi_contracts:
        for buyer_id, items in items_by_buyer.items():
            contract = add_contract_to_tender(
                contract_model, tender, items, value, buyer_id, award,
            )
            contracts_added.append(contract)
    else:  # ignoring "buyer_id", even if not None
        contract_items = []
        for _, items in items_by_buyer.items():
            contract_items.extend(items)
        contract = add_contract_to_tender(
            contract_model, tender, contract_items, value, None, award,
        )
        contracts_added.append(contract)

    return contracts_added


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
    contract_data = contract.serialize()
    tender["contracts"].append(
        contract_data
    )
    return contract_data


def save_contracts_to_contracting(contracts):
    tender = get_tender()
    request = get_request()
    award = get_award()
    for contract in deepcopy(contracts):
        del contract["date"]
        bids = tuple(i for i in tender.get("bids", "") if i["id"] == award.get("bid_id", ""))
        if not bids:

            return
        bid = bids[0]
        extend_contract_data = {
            "buyer": tender["buyer"] if tender.get("buyer") else tender["procuringEntity"],
            "tender_id": tender["_id"],
            "owner": tender["owner"],
            "tender_token": sha512(tender["owner_token"].encode("utf-8")).hexdigest(),
            "bid_owner": bid["owner"],
            "bid_token": bid["owner_token"],
        }
        contract.update(extend_contract_data)
        contract_data = PostContract(contract).serialize()
        save_contract(request, contract=contract_data, contract_src={}, insert=True)
