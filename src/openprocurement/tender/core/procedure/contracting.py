from collections import defaultdict
from copy import deepcopy
from datetime import timedelta
from logging import getLogger
from typing import Dict, List
from urllib.parse import urlparse
from uuid import uuid4

from openprocurement.api.constants_env import REQ_RESPONSE_VALUES_VALIDATION_FROM
from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import (
    calculate_full_date,
    get_contract_by_id,
    request_init_contract,
    upload_contract_pdf,
)
from openprocurement.contracting.core.procedure.models.access import AccessRole
from openprocurement.contracting.core.procedure.models.contract import (
    Buyer,
    ContractValue,
)
from openprocurement.contracting.core.procedure.models.contract import (
    Item as ContractItem,
)
from openprocurement.contracting.core.procedure.models.contract import (
    PostContract,
    Supplier,
)
from openprocurement.contracting.core.procedure.models.document import PostDocument
from openprocurement.contracting.core.procedure.serializers.contract import (
    ContractBaseSerializer,
)
from openprocurement.contracting.core.procedure.utils import save_contract
from openprocurement.tender.core.constants import CONTRACT_PERIOD_START_DAYS
from openprocurement.tender.core.procedure.context import get_award, get_request
from openprocurement.tender.core.procedure.documents import check_document
from openprocurement.tender.core.procedure.utils import prepare_tender_item_for_contract

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
        # None == None in case of non-lots (as no relatedLot nor lotID)
        if item.get("relatedLot") == award.get("lotID") and ("quantity" not in item or item.get("quantity") != 0):
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
        "date": get_request_now().isoformat(),
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
    req_responses = {rr["requirement"]["id"]: rr for rr in bid.get("requirementResponses", "")}

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
                }

                if get_request_now() > REQ_RESPONSE_VALUES_VALIDATION_FROM:
                    if "value" in req_responses[req["id"]]:
                        item_attr["value"] = req_responses[req["id"]]["value"]

                    if "values" in req_responses[req["id"]]:
                        item_attr["values"] = req_responses[req["id"]]["values"]
                else:  # old logic of conversation any responses into values
                    if req_responses[req["id"]].get("values"):
                        item_attr["values"] = req_responses[req["id"]]["values"]
                    else:
                        item_attr["values"] = [req_responses[req["id"]]["value"]]

                if "unit" in req:
                    item_attr["unit"] = req["unit"]

                items_attributes[item_id].append(item_attr)

    for item in contract.get("items", ""):
        if item["id"] in items_attributes:
            item["attributes"] = items_attributes[item["id"]]


def get_buyer(tender, contract):
    if contract.get("buyerID"):
        for i in tender.get("buyers", ""):
            if contract["buyerID"] == i["id"] and "id" in i:
                return deepcopy(i)
    return deepcopy(tender["procuringEntity"])


def get_additional_contract_data(request, contract, tender, award, buyer):
    if "date" in contract:
        del contract["date"]

    clean_objs([buyer], Buyer, {"id", "contactPoint"})
    clean_objs(contract["suppliers"], Supplier, {"id", "contactPoint"})

    bids = tuple(i for i in tender.get("bids", "") if i["id"] == award.get("bid_id", ""))
    if bids:
        bid = bids[0]
        set_attributes_to_contract_items(tender, bid, contract)
    else:
        # For limited procedures
        bid = tender

    contract_data = {
        "mode": tender.get("mode"),
        "buyer": buyer,
        "tender_id": tender["_id"],
        "owner": tender["owner"],
    }

    # eContract check
    if is_econtract(contract, buyer):
        access = [
            {
                "owner": buyer["contract_owner"],
                "role": AccessRole.BUYER,
            },
            {
                "owner": contract["suppliers"][0]["contract_owner"],
                "role": AccessRole.SUPPLIER,
            },
        ]
        contract_period_start_date = calculate_full_date(get_request_now(), timedelta(days=CONTRACT_PERIOD_START_DAYS))
        contract_data.update(
            {
                "access": access,
                "period": {
                    "startDate": contract_period_start_date.isoformat(),
                    # end of current year
                    "endDate": contract_period_start_date.replace(
                        month=12, day=31, hour=23, minute=59, second=59
                    ).isoformat(),
                },
            }
        )
    else:
        contract_data["access"] = [
            {
                "token": tender["owner_token"],
                "owner": tender["owner"],
                "role": AccessRole.TENDER,
            },
            {
                "token": bid["owner_token"],
                "owner": bid["owner"],
                "role": AccessRole.BID,
            },
        ]

    return contract_data


def is_econtract(contract, buyer):
    return "contract_owner" in buyer and "contract_owner" in contract["suppliers"][0]


def save_contracts_to_contracting(contracts, award=None):
    tender = get_tender()
    if not award:
        award = get_award()
    request = get_request()
    for contract in deepcopy(contracts):
        buyer = get_buyer(tender, contract)
        additional_contract_data = get_additional_contract_data(request, contract, tender, award, buyer)
        if not additional_contract_data:
            return
        contract.update(additional_contract_data)
        contract = PostContract(contract).serialize()
        contract["config"] = {
            "restricted": tender["config"]["restricted"],
        }
        if is_econtract(contract, buyer):
            upload_contract_pdf_document(request, contract)
        request_init_contract(request, contract, contract_src={})
        save_contract(request, insert=True)


def update_econtracts_statuses(contracts, status):
    request = get_request()

    for contract in contracts:
        econtract = get_contract_by_id(request, contract["id"], raise_error=False)
        if econtract:
            request_init_contract(request, econtract, contract_src={})
            econtract["status"] = status
            econtract["date"] = get_request_now().isoformat()
            save_contract(request)


def upload_contract_pdf_document(request, contract: dict):
    contract_data = ContractBaseSerializer(contract).data
    document = upload_contract_pdf(request, contract_data)["data"]
    document = PostDocument(document).serialize()
    document["documentType"] = "contractNotice"
    check_document(request, document)
    key = urlparse(document["url"]).path.split("/")[-1]
    document["url"] = request.route_url(
        "EContract Documents",
        contract_id=contract["id"],
        document_id=document["id"],
        _query={"download": key},
    )
    contract["documents"] = contract.get("documents", [])
    contract["documents"].append(document)
