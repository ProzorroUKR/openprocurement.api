from uuid import uuid4
from typing import List, Dict

from openprocurement.tender.core.procedure.context import (
    get_request,
    get_award,
)
from openprocurement.api.procedure.context import get_tender, get_tender_config
from openprocurement.api.context import get_now
from openprocurement.tender.belowthreshold.procedure.utils import prepare_tender_item_for_contract
from openprocurement.api.utils import get_contract_by_id, request_init_contract
from openprocurement.tender.core.procedure.utils import is_new_contracting
from openprocurement.contracting.econtract.procedure.models.contract import PostContract
from openprocurement.contracting.core.procedure.utils import save_contract
from collections import defaultdict
from copy import deepcopy
from logging import getLogger

LOGGER = getLogger(__name__)


def generate_contract_value(award, multi_contracts=False):
    if award.get("value"):
        value = deepcopy(award["value"])
        if multi_contracts:
            value["amountNet"], value["amount"] = 0, 0
        else:
            value["amountNet"] = value["amount"]
        return value
    return None


def add_contracts(request, award):
    # TODO: copy of add_contracts func, now only for pq, later rename on add_contracts

    tender = request.validated["tender"]
    bids = tuple(i for i in tender.get("bids", "") if i["id"] == award.get("bid_id", ""))
    bid = bids[0] if bids else None

    if bid and bid.get("items"):
        items = merge_items(bid["items"], tender["items"])
    else:
        items = tender["items"]

    # split items by relatedBuyer
    items_by_buyer = defaultdict(list)
    for item in items:
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
                tender, items, value, buyer_id, award,
            )
            contracts_added.append(contract)
    else:  # ignoring "buyer_id", even if not None
        contract_items = []
        for _, items in items_by_buyer.items():
            contract_items.extend(items)
        contract = add_contract_to_tender(
            tender, contract_items, value, None, award,
        )
        contracts_added.append(contract)

    return contracts_added


def merge_items(bid_items: List[Dict], tender_items: List[Dict]) -> List[Dict]:
    tender_items = deepcopy(tender_items)
    tender_item_by_id = {i["id"]: i for i in tender_items}
    merged_items = []
    for bid_item in bid_items:
        item = tender_item_by_id.get(bid_item["id"])
        if not item:
            continue
        item.update(bid_item)
        merged_items.append(item)

    return merged_items


def add_contract_to_tender(tender, contract_items, contract_value, buyer_id, award):

    server_id = get_request().registry.server_id
    contract_number = len(tender.get('contracts', '')) + 1
    if "contracts" not in tender:
        tender["contracts"] = []

    base_contract_data = {
        "id": uuid4().hex,
        "status": "pending",
        "awardID": award["id"],
        "date": get_now().isoformat(),
    }
    if contract_value:
        base_contract_data["value"] = contract_value

    contract_data = {
        # "awardID": award["id"],
        "suppliers": award["suppliers"],
        "items": contract_items,
        "buyerID": buyer_id,
        "contractID": f"{tender['tenderID']}-{server_id}{contract_number}",
    }

    if tender.get("contractTemplateName"):
        contract_data["contractTemplateName"] = tender["contractTemplateName"]
    contract_data.update(base_contract_data)

    for k in contract_data.copy():
        if contract_data[k] is None:
            del contract_data[k]

    if is_new_contracting():
        tender["contracts"].append(base_contract_data)
    else:
        tender["contracts"].append(contract_data)

    return contract_data


def delete_buyers_attr(objs):
    for obj in objs:
        for attr in ("kind", "scale", "contactPoint", "id"):
            if attr in obj:
                del obj[attr]


def set_attributes_to_contract_items(tender, bid, contract):
    req_responses = {
        rr["requirement"]["id"]: rr["values"]
        if rr.get("values") else [rr["value"]]
        for rr in bid.get("requirementResponses", "")
    }

    items_attributes = {}
    for c in tender.get("criteria", ""):
        if c.get("relatesTo", "") != "item":
            continue

        item_id = c["relatedItem"]
        if item_id not in items_attributes:
            items_attributes[item_id] = []

        for rg in c.get("requirementGroups", ""):
            for req in rg.get("requirements", ""):
                if req["id"] not in req_responses:
                    continue

                item_attr = {
                    "name": req["title"],
                    "values": req_responses[req["id"]],
                }
                if "unit" in req:
                    item_attr["unit"] = req["unit"]

                items_attributes[item_id].append(item_attr)

    for item in contract["items"]:
        if item["id"] in items_attributes:
            item["attributes"] = items_attributes[item["id"]]


def get_additional_contract_data(request, contract, tender, award):
    if "date" in contract:
        del contract["date"]

    buyer = None
    if contract.get("buyerID"):
        for i in tender.get("buyers", ""):
            if contract["buyerID"] == i["id"] and "id" in i:
                buyer = deepcopy(i)
                break
    else:
        buyer = deepcopy(tender["procuringEntity"])

    delete_buyers_attr([buyer])
    delete_buyers_attr(contract["suppliers"])

    bids = tuple(i for i in tender.get("bids", "") if i["id"] == award.get("bid_id", ""))
    if bids:
        bid = bids[0]
        set_attributes_to_contract_items(tender, bid, contract)
    else:
        # For limited procedures
        bid = tender

    return {
        "buyer": buyer,
        "tender_id": tender["_id"],
        "owner": tender["owner"],
        "tender_token": tender["owner_token"],
        "bid_owner": bid["owner"],
        "bid_token": bid["owner_token"],
    }


def save_contracts_to_contracting(contracts, award=None):
    tender = get_tender()
    tender_config = get_tender_config()
    if not is_new_contracting():
        return
    if not award:
        award = get_award()
    request = get_request()
    for contract in deepcopy(contracts):
        additional_contract_data = get_additional_contract_data(request, contract, tender, award)
        if not additional_contract_data:
            return
        contract.update(additional_contract_data)
        contract_data = PostContract(contract).serialize()
        contract_data["config"] = {
            "restricted": tender_config.get("restricted", False),
        }
        request_init_contract(request, contract_data, contract_src={})
        save_contract(request, insert=True)


def update_econtracts_statuses(contracts_ids, status):
    request = get_request()

    if not is_new_contracting():
        return

    for i in contracts_ids:
        econtract = get_contract_by_id(request, i, raise_error=False)
        if econtract:
            request_init_contract(request, econtract, contract_src={})
            econtract["status"] = status
            econtract["date"] = get_now().isoformat()
            save_contract(request)
