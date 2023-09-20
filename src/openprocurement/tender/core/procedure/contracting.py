from hashlib import sha512
from uuid import uuid4

from openprocurement.tender.core.procedure.context import get_request, get_tender, get_award
from openprocurement.api.context import get_now
from openprocurement.api.utils import context_unpack, get_first_revision_date, get_contract_by_id
from openprocurement.api.constants import PQ_NEW_CONTRACTING_FROM
from openprocurement.tender.belowthreshold.utils import prepare_tender_item_for_contract
from openprocurement.contracting.econtract.procedure.models.contract import PostContract
from openprocurement.contracting.core.procedure.utils import save_contract
from collections import defaultdict
from copy import deepcopy
from logging import getLogger

LOGGER = getLogger(__name__)


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
        contract.serialize()
    )
    return contract_data


def pq_add_contracts(request, award):
    # TODO: copy of add_contracts func, now only for pq, later rename on add_contracts

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
            contract = pq_add_contract_to_tender(
                tender, items, value, buyer_id, award,
            )
            contracts_added.append(contract)
    else:  # ignoring "buyer_id", even if not None
        contract_items = []
        for _, items in items_by_buyer.items():
            contract_items.extend(items)
        contract = pq_add_contract_to_tender(
            tender, contract_items, value, None, award,
        )
        contracts_added.append(contract)

    return contracts_added


def pq_add_contract_to_tender(tender, contract_items, contract_value, buyer_id, award):

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

    contract_data = {
        # "awardID": award["id"],
        "suppliers": award["suppliers"],
        "value": contract_value,
        "items": contract_items,
        "contractID": f"{tender['tenderID']}-{server_id}{contract_number}",
    }
    if buyer_id:
        contract_data["buyerID"] = buyer_id

    if tender.get("contractTemplateUri"):
        contract_data["contractTemplateUri"] = tender["contractTemplateUri"]
    contract_data.update(base_contract_data)

    if get_first_revision_date(tender, default=get_now()) > PQ_NEW_CONTRACTING_FROM:
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

    bids = tuple(i for i in tender.get("bids", "") if i["id"] == award.get("bid_id", ""))
    if not bids:
        LOGGER.exception(f"Bid {award['bid_id']} not found",
                         extra=context_unpack(request, {"MESSAGE_ID": "fail_find_tender_bid"}))
        return

    bid = bids[0]

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

    set_attributes_to_contract_items(tender, bid, contract)

    return {
        "buyer": buyer,
        "tender_id": tender["_id"],
        "owner": tender["owner"],
        "tender_token": sha512(tender["owner_token"].encode("utf-8")).hexdigest(),
        "bid_owner": bid["owner"],
        "bid_token": bid["owner_token"],
    }


def save_contracts_to_contracting(contracts, award=None):
    tender = get_tender()
    if get_first_revision_date(tender, default=get_now()) < PQ_NEW_CONTRACTING_FROM:
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
        save_contract(request, contract=contract_data, contract_src={}, insert=True)


def update_econtracts_statuses(contracts_ids, status):
    tender = get_tender()
    request = get_request()

    if get_first_revision_date(tender, default=get_now()) < PQ_NEW_CONTRACTING_FROM:
        return

    for i in contracts_ids:
        econtract = get_contract_by_id(request, i, raise_error=False)
        if econtract:
            econtract_src = deepcopy(econtract)
            econtract["status"] = status
            econtract["date"] = get_now().isoformat()
            save_contract(request, contract=econtract, contract_src=econtract_src)
