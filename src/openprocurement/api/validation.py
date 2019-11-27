# -*- coding: utf-8 -*-
from schematics.exceptions import ModelValidationError, ModelConversionError, ValidationError
from contextlib import contextmanager
from openprocurement.api.auth import check_user_accreditations, ACCR_TEST, ACCR_EXIT
from openprocurement.api.constants import INN_SCHEME, CPV_PHARM_PRODUCTS, CPV_336_INN_FROM
from openprocurement.api.utils import (
    apply_data_patch,
    update_logging_context,
    error_handler,
    get_now,
    get_first_revision_date,
    get_root,
)

OPERATIONS = {"POST": "add", "PATCH": "update", "PUT": "update", "DELETE": "delete"}


def validate_json_data(request):
    try:
        json = request.json_body
    except ValueError as e:
        request.errors.add("body", "data", str(e))
        request.errors.status = 422
        raise error_handler(request.errors)
    if not isinstance(json, dict) or "data" not in json or not isinstance(json.get("data"), dict):
        request.errors.add("body", "data", "Data not available")
        request.errors.status = 422
        raise error_handler(request.errors)
    request.validated["json_data"] = json["data"]
    return json["data"]


@contextmanager
def handle_data_exceptions(request):
    try:
        yield
    except (ModelValidationError, ModelConversionError) as e:
        for i in e.messages:
            request.errors.add("body", i, e.messages[i])
        request.errors.status = 422
        raise error_handler(request.errors)
    except ValueError as e:
        request.errors.add("body", "data", str(e))
        request.errors.status = 422
        raise error_handler(request.errors)


def validate_data(request, model, partial=False, data=None):
    if data is None:
        data = validate_json_data(request)

    with handle_data_exceptions(request):
        if partial and isinstance(request.context, model):
            initial_data = request.context.serialize()
            m = model(initial_data)
            new_patch = apply_data_patch(initial_data, data)
            if new_patch:
                m.import_data(new_patch, partial=True, strict=True)
            m.__parent__ = request.context.__parent__
            m.validate()
            role = request.context.get_role()
            method = m.to_patch
        else:
            m = model(data)
            m.__parent__ = request.context
            m.validate()
            method = m.serialize
            role = "create"

    if hasattr(type(m), "_options") and role not in type(m)._options.roles:
        request.errors.add("url", "role", "Forbidden")
        request.errors.status = 403
        raise error_handler(request.errors)
    else:
        data = method(role)
        request.validated["data"] = data
        if not partial:
            m = model(data)
            m.__parent__ = request.context
            if model._options.namespace:
                request.validated[model._options.namespace.lower()] = m
            else:
                request.validated[model.__name__.lower()] = m
    return data


def validate_patch_document_data(request):
    model = type(request.context)
    return validate_data(request, model, True)


def validate_document_data(request):
    context = request.context if "documents" in request.context else request.context.__parent__
    model = type(context).documents.model_class
    return validate_data(request, model)


def validate_file_upload(request):
    update_logging_context(request, {"document_id": "__new__"})
    if request.registry.docservice_url and request.content_type == "application/json":
        return validate_document_data(request)
    if "file" not in request.POST or not hasattr(request.POST["file"], "filename"):
        request.errors.add("body", "file", "Not Found")
        request.errors.status = 404
        raise error_handler(request.errors)
    else:
        request.validated["file"] = request.POST["file"]


def validate_file_update(request):
    if request.registry.docservice_url and request.content_type == "application/json":
        return validate_document_data(request)
    if request.content_type == "multipart/form-data":
        validate_file_upload(request)


def validate_items_uniq(items, *args):
    if items:
        ids = [i.id for i in items]
        if [i for i in set(ids) if ids.count(i) > 1]:
            raise ValidationError(u"Item id should be uniq for all items")


def validate_cpv_group(items, *args):
    if items and len(set([i.classification.id[:3] for i in items])) != 1:
        raise ValidationError(u"CPV group of items be identical")


def validate_classification_id(items, *args):
    for item in items:
        if get_first_revision_date(get_root(item["__parent__"]), default=get_now()) > CPV_336_INN_FROM:
            schemes = [x.scheme for x in item.additionalClassifications]
            schemes_inn_count = schemes.count(INN_SCHEME)
            if item.classification.id == CPV_PHARM_PRODUCTS and schemes_inn_count != 1:
                raise ValidationError(
                    u"Item with classification.id={} have to contain exactly one additionalClassifications "
                    u"with scheme={}".format(CPV_PHARM_PRODUCTS, INN_SCHEME)
                )
            if item.classification.id.startswith(CPV_PHARM_PRODUCTS[:3]) and schemes_inn_count > 1:
                raise ValidationError(
                    u"Item with classification.id that starts with {} and contains additionalClassification "
                    u"objects have to contain no more than one additionalClassifications "
                    u"with scheme={}".format(CPV_PHARM_PRODUCTS[:3], INN_SCHEME)
                )


def validate_accreditation_level(request, levels, location, name, action):
    if not request.check_accreditations(levels):
        request.errors.add(
            location, "accreditation", "Broker Accreditation level does not permit {} {}".format(name, action)
        )
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_accreditation_level_mode(request, mode, location, name, action):
    if mode is None and request.check_accreditations((ACCR_TEST,)):
        request.errors.add(
            location, "mode", "Broker Accreditation level does not permit {} {}".format(name, action)
        )
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_accreditation_level_owner(request, owner, location, name, action):
    if not check_user_accreditations(request, owner, (ACCR_EXIT,), default=True):
        request.errors.add(
            location, "accreditation", "Owner Accreditation level does not permit {} {}".format(name, action)
        )
        request.errors.status = 403
        raise error_handler(request.errors)
