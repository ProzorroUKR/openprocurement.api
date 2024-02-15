from logging import getLogger
from hashlib import sha512

from openprocurement.api.utils import (
    context_unpack,
    get_now,
    handle_store_exceptions,
)
from openprocurement.api.auth import extract_access_token

from openprocurement.tender.core.procedure.utils import (
    set_mode_test_titles,
)
from openprocurement.api.procedure.utils import append_revision, get_revision_changes, is_item_owner

LOGGER = getLogger("openprocurement.contracting.api.procedure")


def save_contract(request, insert=False, contract=None, contract_src=None):
    if contract is None:
        contract = request.validated["contract"]
    if contract_src is None:
        contract_src = request.validated["contract_src"]

    if contract.get("mode", "") == "test":
        set_mode_test_titles(contract)

    patch = get_revision_changes(contract, contract_src)
    if patch:
        now = get_now()
        append_revision(request, contract, patch)
        old_date_modified = contract.get("dateModified", now.isoformat())
        with handle_store_exceptions(request):
            request.registry.mongodb.contracts.save(
                contract,
                insert=insert,
                modified=True,
            )
            LOGGER.info(
                "Saved contract {}: dateModified {} -> {}".format(
                    contract["_id"], old_date_modified, contract["dateModified"]
                ),
                extra=context_unpack(request, {"MESSAGE_ID": "save_contract"}, {"CONTRACT_REV": contract["_rev"]}),
            )
            return True


def is_owner_by_fields(request, contract, token_field, owner_field):
    acc_token = extract_access_token(request)
    tender_token = contract[token_field]
    if acc_token and len(tender_token) != len(acc_token):
        acc_token = sha512(acc_token.encode("utf-8")).hexdigest()
    return request.authenticated_userid == contract[owner_field] and acc_token == tender_token


def is_tender_owner(request, contract):
    return is_owner_by_fields(request, contract, "tender_token", "owner")


def is_contract_owner(request, contract):
    return is_tender_owner(request, contract) or is_item_owner(request, contract)


def is_bid_owner(request, contract):
    return is_owner_by_fields(request, contract, "bid_token", "bid_owner")
