from collections import defaultdict
from copy import deepcopy
from logging import getLogger
from typing import Dict, List
from uuid import uuid4

from openprocurement.api.context import get_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import get_contract_by_id, request_init_contract
from openprocurement.contracting.core.procedure.utils import save_contract
from openprocurement.contracting.econtract.procedure.models.contract import (
    Buyer,
    ContractValue,
)
from openprocurement.contracting.econtract.procedure.models.contract import (
    Item as ContractItem,
)
from openprocurement.contracting.econtract.procedure.models.contract import (
    PostContract,
    Supplier,
)
from openprocurement.tender.belowthreshold.procedure.utils import (
    prepare_tender_item_for_contract,
)
from openprocurement.tender.core.procedure.context import get_award, get_request

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
                tender,
                items,
                value,
                buyer_id,
                award,
            )
            contracts_added.append(contract)
    else:  # ignoring "buyer_id", even if not None
        contract_items = []
        for _, items in items_by_buyer.items():
            contract_items.extend(items)
        contract = add_contract_to_tender(
            tender,
            contract_items,
            value,
            None,
            award,
        )
        contracts_added.append(contract)

    return contracts_added


def merge_items(bid_items: List[Dict], tender_items: List[Dict]) -> List[Dict]:
    tender_items = deepcopy(tender_items)
    tender_item_by_id = {i["id"]: i for i in tender_items}
    for bid_item in bid_items:
        item = tender_item_by_id.get(bid_item["id"])
        if not item:
            continue
        item.update(bid_item)

    return list(tender_item_by_id.values())


def add_contract_to_tender(tender, contract_items, contract_value, buyer_id, award):
    server_id = get_request().registry.server_id
    contract_number = len(tender.get("contracts", "")) + 1
    if "contracts" not in tender:
        tender["contracts"] = []

    base_contract_data = {
        "id": uuid4().hex,
        "status": "pending",
        "awardID": award["id"],
        "date": get_now().isoformat(),
        "contractID": f"{tender['tenderID']}-{server_id}{contract_number}",
    }
    if contract_value:
        base_contract_data["value"] = clean_contract_value(contract_value)

    contract_data = {
        # "awardID": award["id"],
        "suppliers": award["suppliers"],
        "buyerID": buyer_id,
    }
    if contract_items:
        contract_data["items"] = clean_objs(deepcopy(contract_items), ContractItem)

    if tender.get("contractTemplateName"):
        contract_data["contractTemplateName"] = tender["contractTemplateName"]
    contract_data.update(base_contract_data)

    for k in contract_data.copy():
        if contract_data[k] is None:
            del contract_data[k]

    tender["contracts"].append(base_contract_data)

    return contract_data


def clean_objs(objs: List[Dict], model, forbidden_fields=None):
    if not objs:
        return

    if not forbidden_fields:
        forbidden_fields = {}

    acceptable_fields = set(model.fields)
    for obj in objs:
        for field in set(obj.keys()):
            if field not in acceptable_fields or field in forbidden_fields:
                obj.pop(field, None)
    return objs


def clean_contract_value(value: dict) -> dict:
    acceptable_fields = set(ContractValue.fields)
    for field in set(value.keys()):
        if field not in acceptable_fields:
            value.pop(field, None)
    return value


def set_attributes_to_contract_items(tender, bid, contract):
    req_responses = {
        rr["requirement"]["id"]: rr["values"] if rr.get("values") else [rr["value"]]
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

                if req.get("status", "active") != "active":
                    continue

                item_attr = {
                    "name": req["title"],
                    "values": req_responses[req["id"]],
                }
                if "unit" in req:
                    item_attr["unit"] = req["unit"]

                items_attributes[item_id].append(item_attr)

    for item in contract.get("items", ""):
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

    clean_objs([buyer], Buyer, {"id", "contactPoint"})
    clean_objs(contract["suppliers"], Supplier, {"id", "contactPoint"})

    bids = tuple(i for i in tender.get("bids", "") if i["id"] == award.get("bid_id", ""))
    if bids:
        bid = bids[0]
        set_attributes_to_contract_items(tender, bid, contract)
    else:
        # For limited procedures
        bid = tender

    return {
        "mode": tender.get("mode"),
        "buyer": buyer,
        "tender_id": tender["_id"],
        "owner": tender["owner"],
        "tender_token": tender["owner_token"],
        "bid_owner": bid["owner"],
        "bid_token": bid["owner_token"],
    }


def save_contracts_to_contracting(contracts, award=None):
    tender = get_tender()
    if not award:
        award = get_award()
    request = get_request()
    for contract in deepcopy(contracts):
        additional_contract_data = get_additional_contract_data(request, contract, tender, award)
        if not additional_contract_data:
            return
        contract.update(additional_contract_data)
        contract = PostContract(contract).serialize()
        contract["config"] = {
            "restricted": tender["config"]["restricted"],
        }
        request_init_contract(request, contract, contract_src={})
        save_contract(request, insert=True)


def update_econtracts_statuses(contracts_ids, status):
    request = get_request()

    for i in contracts_ids:
        econtract = get_contract_by_id(request, i, raise_error=False)
        if econtract:
            request_init_contract(request, econtract, contract_src={})
            econtract["status"] = status
            econtract["date"] = get_now().isoformat()
            save_contract(request)
