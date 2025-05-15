from hashlib import sha512

from openprocurement.api.auth import extract_access_token
from openprocurement.api.procedure.utils import (
    append_revision,
    get_revision_changes,
    is_item_owner,
    save_object,
)


def save_contract(request, insert=False):
    obj = request.validated["contract"]
    obj_src = request.validated["contract_src"]

    patch = get_revision_changes(obj, obj_src)
    if not patch:
        return False

    append_revision(request, obj, patch)

    return save_object(request, "contract", insert=insert)


def is_owner_by_fields(request, item, token_field="token", owner_field="owner"):
    acc_token = extract_access_token(request)
    tender_token = item.get(token_field)
    if tender_token and acc_token and len(tender_token) != len(acc_token):
        acc_token = sha512(acc_token.encode("utf-8")).hexdigest()
    return request.authenticated_userid == item.get(owner_field) and acc_token and acc_token == tender_token


def is_tender_owner(request, contract):
    return is_owner_by_fields(request, contract, "tender_token")


def is_contract_owner(request, contract):
    return (
        is_tender_owner(request, contract)
        or ("owner_token" in contract and is_item_owner(request, contract))
        or is_owner_by_fields(request, contract.get("access", {}).get("buyer", {}))
    )


def is_bid_owner(request, contract):
    return is_owner_by_fields(request, contract, "bid_token", "bid_owner") or is_owner_by_fields(
        request, contract.get("access", {}).get("supplier", {})
    )
