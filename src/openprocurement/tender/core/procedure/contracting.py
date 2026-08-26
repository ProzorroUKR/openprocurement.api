from collections import defaultdict
from copy import deepcopy
from datetime import timedelta
from logging import getLogger
from typing import Dict, List
from uuid import uuid4

from openprocurement.api.constants_env import REQ_RESPONSE_VALUES_VALIDATION_FROM
from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.value import AmountPercentageValue
from openprocurement.api.utils import (
    calculate_full_date,
    get_contract_by_id,
    request_init_contract,
    upload_contract_change_pdf,
    upload_contract_pdf,
)
from openprocurement.contracting.core.procedure.models.access import AccessRole
from openprocurement.contracting.core.procedure.models.contract import (
    Buyer,
    ContractValue,
    PostContract,
    Supplier,
)
from openprocurement.contracting.core.procedure.models.contract import (
    Item as ContractItem,
)
from openprocurement.contracting.core.procedure.models.document import PostDocument
from openprocurement.contracting.core.procedure.serializers.contract import (
    ContractBaseSerializer,
)
from openprocurement.contracting.core.procedure.utils import save_contract
from openprocurement.tender.core.constants import CONTRACT_PERIOD_START_DAYS
from openprocurement.tender.core.procedure.context import get_award, get_request
from openprocurement.tender.core.procedure.documents import (
    check_document,
    update_document_url,
)
from openprocurement.tender.core.procedure.serializers.tender import (
    TenderBaseSerializer,
)
from openprocurement.tender.core.procedure.utils import prepare_tender_item_for_contract

LOGGER = getLogger(__name__)


def generate_contract_value(award, multi_contracts=False):
    if award.get("value"):
        value = deepcopy(award["value"])
        if "amountPercentage" in value:
            return value
        if multi_contracts:
            value["amountNet"], value["amount"] = 0, 0
        else:
            value["amountNet"] = value["amount"]
        return value
    return None


def add_contracts(request, award):
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

    # copy from tender all related lot milestones + tender related milestones, without relatedLot field
    lot_id = award.get("lotID")
    milestones = [
        {k: v for k, v in i.items() if k not in ("relatedLot",)}
        for i in filter(lambda x: x.get("relatedLot") in (lot_id, None), tender.get("milestones", []))
    ]
    milestones = [{**x, "status": "scheduled"} for x in milestones]

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
                milestones,
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
            milestones,
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


def drop_none_values(data):
    """Remove keys with None values recursively so missing fields stay omitted."""
    if isinstance(data, dict):
        for key, value in list(data.items()):
            if value is None:
                del data[key]
            else:
                drop_none_values(value)
    elif isinstance(data, list):
        for item in data:
            drop_none_values(item)
    return data


def add_contract_to_tender(tender, contract_items, contract_value, buyer_id, award, contract_milestones):
    contract_number = len(tender.get("contracts", "")) + 1
    if "contracts" not in tender:
        tender["contracts"] = []

    lot = None
    if related_lot_id := award.get("lotID"):
        for lot in tender.get("lots", []):
            if lot["id"] == related_lot_id:
                break
        else:
            lot = None

    base_contract_data = {
        "id": uuid4().hex,
        "status": "pending",
        "awardID": award["id"],
        "date": get_request_now().isoformat(),
        "contractID": f"{tender['tenderID']}-a{contract_number}",
    }

    source = lot or tender
    for field in ("title", "title_en", "description", "description_en"):
        value = source.get(field)
        if value is not None:
            base_contract_data[field] = value

    if contract_value:
        base_contract_data["value"] = clean_contract_value(contract_value)

    contract_data = {
        # "awardID": award["id"],
        "suppliers": award["suppliers"],
        "buyerID": buyer_id,
        "milestones": contract_milestones,
    }
    if contract_items:
        contract_data["items"] = clean_objs(deepcopy(contract_items), ContractItem)

    if tender.get("contractTemplateName"):
        contract_data["contractTemplateName"] = tender["contractTemplateName"]
    contract_data.update(base_contract_data)

    drop_none_values(contract_data)
    drop_none_values(base_contract_data)

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
        drop_none_values(obj)
    return objs


def clean_contract_value(value: dict) -> dict:
    if "amountPercentage" in value:
        acceptable_fields = set(AmountPercentageValue.fields)
    else:
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
        "buyer": buyer,
        "tender_id": tender["_id"],
        "owner": tender["owner"],
    }

    if tender.get("mode"):
        contract_data["mode"] = tender["mode"]

    if tender.get("contractChangeRationaleTypes"):
        contract_data["contractChangeRationaleTypes"] = tender["contractChangeRationaleTypes"]

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


def prepare_contracts_added(contracts, award=None):
    tender = get_tender()
    if not award:
        award = get_award()
    request = get_request()
    prepared = []
    for contract in deepcopy(contracts):
        buyer = get_buyer(tender, contract)
        additional_contract_data = get_additional_contract_data(request, contract, tender, award, buyer)
        if not additional_contract_data:
            break
        contract.update(additional_contract_data)
        drop_none_values(contract)
        contract = PostContract(contract).serialize()
        drop_none_values(contract)
        contract["config"] = {
            "restricted": tender["config"]["restricted"],
        }
        if is_econtract(contract, buyer):
            upload_contract_pdf_document(contract, tender)
        prepared.append(contract)
    return prepared


def prepare_contracts_cancelled(contracts):
    request = get_request()
    prepared = []
    for contract in contracts:
        contract_src = get_contract_by_id(request, contract["id"], raise_error=False)
        if not contract_src:
            continue
        contract_src = deepcopy(contract_src)
        contract = deepcopy(contract_src)
        for cancellation in contract.get("cancellations", []):
            if cancellation["status"] == "pending" and cancellation["reasonType"] == "signingRefusal":
                cancellation["status"] = "active"
        contract["status"] = "cancelled"
        contract["date"] = get_request_now().isoformat()
        prepared.append((contract_src, contract))
    return prepared


def append_contracts_added(request, contracts):
    contracts_added = request.validated.get("contracts_added", [])
    contracts_added.extend(contracts)
    request.validated["contracts_added"] = contracts_added


def append_contracts_cancelled(request, contracts):
    contracts_cancelled = request.validated.get("contracts_cancelled", [])
    contracts_cancelled.extend(contracts)
    request.validated["contracts_cancelled"] = contracts_cancelled


def prepare_contracting_contracts_added(request, tender, award=None):
    contracts_added = request.validated.get("contracts_added")
    if not contracts_added:
        return None
    if award is not None:
        return prepare_contracts_added(contracts_added, award)
    awards_by_id = {a["id"]: a for a in tender.get("awards", "")}
    contracts_by_award = defaultdict(list)
    for contract in contracts_added:
        contracts_by_award[contract["awardID"]].append(contract)
    prepared = []
    for award_id, award_contracts in contracts_by_award.items():
        if award := awards_by_id.get(award_id):
            prepared.extend(prepare_contracts_added(award_contracts, award))
    return prepared or None


def prepare_contracting_contracts_cancelled(request):
    contracts_cancelled = request.validated.get("contracts_cancelled")
    if not contracts_cancelled:
        return None
    prepared = prepare_contracts_cancelled(contracts_cancelled)
    return prepared or None


def create_contracting_contracts(contracts):
    if not contracts:
        return
    request = get_request()
    for contract in contracts:
        request_init_contract(request, contract, contract_src={})
        save_contract(request, insert=True)


def save_contracting_contracts(contracts):
    if not contracts:
        return
    request = get_request()
    for contract_src, contract in contracts:
        request_init_contract(request, contract, contract_src=contract_src)
        save_contract(request)


def upload_contract_pdf_document(contract: dict, tender: dict):
    request = get_request()
    contract_data = ContractBaseSerializer(contract, tender=tender).data
    tender_data = TenderBaseSerializer(tender).data
    data = {
        "contract": contract_data,
        "tender": tender_data,
    }
    document = upload_contract_pdf(request, data)["data"]
    document = PostDocument(document).serialize()
    document["documentType"] = "contractNotice"
    check_document(request, document)
    document_route = "EContract Documents"
    route_kwargs = {"contract_id": contract["id"]}
    update_document_url(request, document, document_route, route_kwargs)
    contract["documents"] = contract.get("documents", [])
    contract["documents"].append(document)


def upload_contract_change_pdf_document(change: dict, contract: dict, tender: dict):
    request = get_request()
    contract_data = ContractBaseSerializer(contract, tender=tender).data
    tender_data = TenderBaseSerializer(tender).data
    data = {
        "change": change,
        "contract": contract_data,
        "tender": tender_data,
    }
    document = upload_contract_change_pdf(request, data)["data"]
    document = PostDocument(document).serialize()
    document["documentOf"] = "change"
    document["documentType"] = "contractNotice"
    check_document(request, document)
    document_route = "EContract change documents"
    route_kwargs = {"contract_id": contract_data["id"], "change_id": change["id"]}
    update_document_url(request, document, document_route, route_kwargs)
    change["documents"] = change.get("documents", [])
    change["documents"].append(document)
