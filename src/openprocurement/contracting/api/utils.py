# -*- coding: utf-8 -*-
from functools import partial
from logging import getLogger
from hashlib import sha512
from cornice.resource import resource
from schematics.types import StringType

from openprocurement.api.mask import mask_object_data
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
    update_logging_context,
)
from openprocurement.tender.core.utils import extract_path

from openprocurement.contracting.api.traversal import factory
from openprocurement.api.validation import validate_json_data


contractingresource = partial(resource, error_handler=error_handler, factory=factory)

LOGGER = getLogger("openprocurement.contracting.api")


def extract_contract_id(request):
    if request.matchdict and "contract_id" in request.matchdict:
        return request.matchdict.get("contract_id")

    path = extract_path(request)
    # extract tender id
    parts = path.split("/")
    if len(parts) < 5 or parts[3] != "contracts":
        return
    tender_id = parts[4]
    return tender_id


def extract_contract_doc(request):
    db = request.registry.mongodb.contracts
    contract_id = extract_contract_id(request)
    if contract_id:
        doc = db.get(contract_id)
        if doc is None:
            request.errors.add("url", "contract_id", "Not Found")
            request.errors.status = 404
            raise error_handler(request)

        mask_object_data(request, doc)  # war time measures

        return doc


def extract_contract(request):
    doc = request.contract_doc
    if doc:
        return request.contract_from_data(doc)


def resolve_contract_model(request, data=None, raise_error=True):
    if data is None:
        data = request.contract_doc

    contract_type = "econtract" if data.get("buyer") else "general"
    # procurement_method_type = data.get("procurementMethodType", "belowThreshold")
    model = request.registry.contract_types.get(contract_type)
    if model is None and raise_error:
        request.errors.add("body", "type", "Not implemented")
        request.errors.status = 415
        raise error_handler(request)
    update_logging_context(request, {"contract_type": contract_type})
    return model


def contract_from_data(request, data, raise_error=True, create=True):
    model = resolve_contract_model(request, data, raise_error)
    if create:
        return model(data)
    return model


def contract_serialize(request, contract_data, fields):
    contract = request.contract_from_data(contract_data, raise_error=False)
    contract.__parent__ = request.context
    return dict([(i, j) for i, j in contract.serialize("view").items() if i in fields])


def save_contract(request, insert=False):
    contract = request.validated["contract"]

    if contract.mode == "test":
        set_modetest_titles(contract)

    patch = get_revision_changes(contract.serialize("plain"), request.validated["contract_src"])
    if patch:
        append_revision(request, contract, patch)

        old_date_modified = contract.dateModified
        with handle_store_exceptions(request):
            request.registry.mongodb.contracts.save(
                contract.to_primitive(),
                insert=insert,
                modified=True,
            )
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
        item.transfer_token = sha512(transfer.encode("utf-8")).hexdigest()
        access["transfer"] = transfer
    return access


def upload_file_to_transaction(request):

    document = request.validated["document"]
    check_document(request, document)

    document_route = request.matched_route.name.replace("collection_", "")
    document = update_document_url(request, document, document_route, {})

    return document


def get_transaction_by_id(request):
    transaction_id = request.matchdict["transaction_id"]
    contract = request.validated["contract"]
    transactions = contract.implementation.transactions

    _transaction = next((trans for trans in transactions if trans["id"] == transaction_id), None)
    return _transaction


class isContract(object):
    """ Route predicate factory for contractType route predicate. """

    def __init__(self, val, config):
        self.val = val

    def text(self):
        return "contractType = %s" % (self.val,)

    phash = text

    def __call__(self, context, request):
        if request.contract_doc is not None:
            contract_type = "econtract" if request.contract_doc.get("buyer") else "general"
            return contract_type == self.val

        # that's how we can have a "POST /tender" view for every tender type
        if request.method == "POST" and request.path.endswith("/tenders"):
            data = validate_json_data(request)
            contract_type = "econtract" if data.get("buyer") else "general"
            return contract_type == self.val

        return False


def register_contract_type(config, model):
    """Register a contract type.
    :param config:
        The pyramid configuration object that will be populated.
    :param model:
        The tender model class
    """
    contract_type = "econtract" if hasattr(model, "buyer") else "general"
    config.registry.contract_types[contract_type] = model