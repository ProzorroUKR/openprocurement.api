import logging
from schematics.exceptions import ModelValidationError
from pyramid.compat import decode_path_info
from pyramid.exceptions import URLDecodeError
from openprocurement.agreement.core.interfaces import IAgreement
from openprocurement.agreement.core.constants import DEFAULT_TYPE
from openprocurement.api.utils import (
    set_modetest_titles,
    get_revision_changes,
    apply_data_patch,
    get_now,
    context_unpack,
    generate_id,
    error_handler,
    handle_store_exceptions,
    append_revision,
)


LOGGER = logging.getLogger("openprocurement.agreement.core")


def agreement_serialize(request, agreement_data, fields):
    agreement = request.agreement_from_data(agreement_data, raise_error=False)
    agreement.__parent__ = request.context
    return {i: j for i, j in agreement.serialize("view").items() if i in fields}


def agreement_from_data(request, data, raise_error=True, create=True):
    agreement_type = data.get("agreementType", DEFAULT_TYPE)
    model = request.registry.agreements_types.get(agreement_type)
    if model is None and raise_error:
        request.errors.add("body", "agreementType", "Not implemented")
        request.errors.status = 415
        raise error_handler(request)
    if model is not None and create:
        model = model(data)
    return model


def extract_agreement_by_id(request, agreement_id):
    db = request.registry.db
    doc = db.get(agreement_id)
    if doc is not None and doc.get("doc_type") == "agreement":
        request.errors.add("url", "agreement_id", "Archived")
        request.errors.status = 410
        raise error_handler(request)
    elif doc is None or doc.get("doc_type") != "Agreement":
        request.errors.add("url", "agreement_id", "Not Found")
        request.errors.status = 404
        raise error_handler(request)
    return request.agreement_from_data(doc)


def extract_agreement(request):
    try:
        # empty if mounted under a path in mod_wsgi, for example
        path = decode_path_info(request.environ["PATH_INFO"] or "/")
    except KeyError:
        path = "/"
    except UnicodeDecodeError as e:
        raise URLDecodeError(e.encoding, e.object, e.start, e.end, e.reason)

    # extract agreement id
    parts = path.split("/")
    if len(parts) < 4 or parts[3] != "agreements":
        return

    agreement_id = parts[4]
    return extract_agreement_by_id(request, agreement_id)


def register_agreement_type(config, model):
    agreement_type = model.agreementType.default or DEFAULT_TYPE
    config.registry.agreements_types[agreement_type] = model


def save_agreement(request):
    """
    Save agreement object to database
    :param request:
    :return: True if Ok
    """
    agreement = request.validated["agreement"]

    if agreement.mode == "test":
        set_modetest_titles(agreement)

    patch = get_revision_changes(agreement.serialize("plain"), request.validated["agreement_src"])
    if patch:
        append_revision(request, agreement, patch)
        old_date_modified = agreement.dateModified
        agreement.dateModified = get_now()

        with handle_store_exceptions(request):
            agreement.store(request.registry.db)
            LOGGER.info(
                "Saved agreement {}: dateModified {} -> {}".format(
                    agreement.id,
                    old_date_modified and old_date_modified.isoformat(),
                    agreement.dateModified.isoformat(),
                ),
                extra=context_unpack(request, {"MESSAGE_ID": "save_agreement"}, {"AGREEMENT_REV": agreement.rev}),
            )
            return True


def apply_patch(request, data=None, save=True, src=None):
    data = request.validated["data"] if data is None else data
    patch = data and apply_data_patch(src or request.context.serialize(), data)
    if patch:
        request.context.import_data(patch)
        if save:
            return save_agreement(request)


def set_ownership(item, request):
    item.owner_token = generate_id()


def get_agreement(model):
    while not IAgreement.providedBy(model):
        model = model.__parent__
    return model
