# -*- coding: utf-8 -*-
from functools import partial
from logging import getLogger
from hashlib import sha512
from cornice.resource import resource
from schematics.types import StringType

from openprocurement.api.utils import (
    error_handler,
    get_revision_changes,
    context_unpack,
    apply_data_patch,
    generate_id,
    set_modetest_titles,
    get_now,
    handle_store_exceptions,
    append_revision,
    check_document,
    update_document_url,
)

from openprocurement.contracting.api.traversal import factory
from openprocurement.contracting.api.models import Contract


contractingresource = partial(resource, error_handler=error_handler, factory=factory)

LOGGER = getLogger("openprocurement.contracting.api")


def extract_contract(request):
    db = request.registry.db
    contract_id = request.matchdict["contract_id"]
    doc = db.get(contract_id)
    if doc is not None and doc.get("doc_type") == "contract":
        request.errors.add("url", "contract_id", "Archived")
        request.errors.status = 410
        raise error_handler(request.errors)
    elif doc is None or doc.get("doc_type") != "Contract":
        request.errors.add("url", "contract_id", "Not Found")
        request.errors.status = 404
        raise error_handler(request.errors)

    return request.contract_from_data(doc)


def contract_from_data(request, data, raise_error=True, create=True):
    if create:
        return Contract(data)
    return Contract


def contract_serialize(request, contract_data, fields):
    contract = request.contract_from_data(contract_data, raise_error=False)
    contract.__parent__ = request.context
    return dict([(i, j) for i, j in contract.serialize("view").items() if i in fields])


def save_contract(request):
    """ Save contract object to database
    :param request:
    :return: True if Ok
    """
    contract = request.validated["contract"]

    if contract.mode == u"test":
        set_modetest_titles(contract)

    patch = get_revision_changes(contract.serialize("plain"), request.validated["contract_src"])
    if patch:
        append_revision(request, contract, patch)

        old_date_modified = contract.dateModified
        contract.dateModified = get_now()

        with handle_store_exceptions(request):
            contract.store(request.registry.db)
            LOGGER.info(
                "Saved contract {}: dateModified {} -> {}".format(
                    contract.id,
                    old_date_modified and old_date_modified.isoformat(),
                    contract.dateModified.isoformat()
                ),
                extra=context_unpack(request, {"MESSAGE_ID": "save_contract"}, {"CONTRACT_REV": contract.rev}),
            )
            return True


def apply_patch(request, data=None, save=True, src=None):
    data = request.validated["data"] if data is None else data
    patch = data and apply_data_patch(src or request.context.serialize(), data)
    if patch:
        request.context.import_data(patch)
        if save:
            return save_contract(request)


def set_ownership(item, request):
    item.owner_token = generate_id()
    access = {"token": item.owner_token}
    if isinstance(getattr(type(item), "transfer_token", None), StringType):
        transfer = generate_id()
        item.transfer_token = sha512(transfer).hexdigest()
        access["transfer"] = transfer
    return access


def upload_file_to_transaction(request):

    document = request.validated["document"]
    check_document(request, document, "body")

    document_route = request.matched_route.name.replace("collection_", "")
    document = update_document_url(request, document, document_route, {})

    return document


def get_transaction_by_id(request):
    transaction_id = request.matchdict["transaction_id"]
    contract = request.validated["contract"]
    transactions = contract.implementation.transactions

    _transaction = next((trans for trans in transactions if trans["id"] == transaction_id), None)
    return _transaction
