# -*- coding: utf-8 -*-
from json import JSONDecodeError

from schematics.exceptions import ValidationError, ModelValidationError
from openprocurement.api.auth import check_user_accreditations, ACCR_TEST, ACCR_EXIT
from openprocurement.api.constants import INN_SCHEME, CPV_PHARM_PRODUCTS, CPV_336_INN_FROM
from openprocurement.api.utils import (
    apply_data_patch,
    update_logging_context,
    error_handler,
    get_now,
    get_first_revision_date,
    get_root,
    handle_data_exceptions,
    raise_operation_error,
)

OPERATIONS = {"POST": "add", "PATCH": "update", "PUT": "update", "DELETE": "delete"}


def validate_json_data(request, allow_bulk=False):
    try:
        json = request.json
    except JSONDecodeError as e:
        request.errors.add("body", "data", str(e))
        # request.errors.add("body", "data", "No JSON object could be decoded")  # Expecting value: line 1 column 1 (char 0)
        request.errors.status = 422
        raise error_handler(request)
    data = json.get("data") if isinstance(json, dict) else None
    allowed_types = (list, dict) if allow_bulk else dict
    if any([
        not isinstance(data, allowed_types),
        isinstance(data, list) and not data,
        isinstance(data, list) and not all(isinstance(i, dict) for i in data)
    ]):
        request.errors.add("body", "data", "Data not available")
        request.errors.status = 422
        raise error_handler(request)
    request.validated["json_data"] = data
    return data


def validate_object_data(request, model, partial=False, data=None, allow_bulk=False):
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
        raise error_handler(request)
    else:
        data = method(role)
        request.validated["data"] = data
        if not partial:
            m = model(data)
            m.__parent__ = request.context
            validated_name = get_model_namespace(model).lower()
            if allow_bulk:
                request.validated["{}_bulk".format(validated_name)] = [m]
            else:
                request.validated[validated_name] = m
    return data


def validate_post_list_data(request, model, data=None):
    with handle_data_exceptions(request):
        valid_data = []
        valid_models = []
        errors = {}

        for i, el in enumerate(data):
            m = model(el)
            m.__parent__ = request.context
            try:
                m.validate()
            except ModelValidationError as err:
                errors[i] = err.messages
            valid_models.append(m)
            valid_data.append(m.serialize("create"))

        if errors:
            raise ModelValidationError(errors)

    if hasattr(type(m), "_options") and "create" not in type(m)._options.roles:
        request.errors.add("url", "role", "Forbidden")
        request.errors.status = 403
        raise error_handler(request)

    request.validated["data"] = data
    valid_models = [model(i) for i in valid_data]
    validated_name = "{}_bulk".format(get_model_namespace(model).lower())
    request.validated[validated_name] = valid_models
    return data


def get_model_namespace(model):
    if model._options.namespace:
        return model._options.namespace
    else:
        return model.__name__.lower()


def validate_data(
    request, model, partial=False, data=None,
    allow_bulk=False, force_bulk=False
):
    """
    function that validate input data for view
    @param request: pyramid.request.Request object
    @param model: api.models.Model object
    @param partial: boolean
    @param data: None or dict
    @param allow_bulk: boolean, allow bulk create
    @param force_bulk: boolean, force bulk even on single data dict
    @return: list or dict
    """
    if data is None:
        data = validate_json_data(request, allow_bulk=allow_bulk)
    if request.method == "POST" and isinstance(data, list) and allow_bulk:
        data = validate_post_list_data(request, model, data)
    else:
        data = validate_object_data(request, model, partial, data, allow_bulk=force_bulk)
    return data


def validate_patch_document_data(request, **kwargs):
    model = type(request.context)
    return validate_data(request, model, True)


def validate_document_data(request, allow_bulk=False):
    context = request.context if "documents" in request.context else request.context.__parent__
    model = type(context).documents.model_class
    return validate_data(request, model, allow_bulk=allow_bulk)


def validate_file_upload(request, **kwargs):
    update_logging_context(request, {"document_id": "__new__"})
    if request.registry.docservice_url and request.content_type == "application/json":
        return validate_document_data(request, allow_bulk=True)
    if "file" not in request.POST or not hasattr(request.POST["file"], "filename"):
        request.errors.add("body", "file", "Not Found")
        request.errors.status = 404
        raise error_handler(request)
    else:
        request.validated["file"] = request.POST["file"]


def validate_file_update(request, **kwargs):
    if request.registry.docservice_url and request.content_type == "application/json":
        return validate_document_data(request)
    if request.content_type == "multipart/form-data":
        validate_file_upload(request)


def validate_items_uniq(items, *args):
    if items:
        ids = [i.id for i in items]
        if [i for i in set(ids) if ids.count(i) > 1]:
            raise ValidationError("Item id should be uniq for all items")


def validate_cpv_group(items, *args):
    if items and len(set([i.classification.id[:3] for i in items])) != 1:
        raise ValidationError("CPV group of items be identical")


def validate_classification_id(items, *args):
    for item in items:
        if get_first_revision_date(get_root(item["__parent__"]), default=get_now()) > CPV_336_INN_FROM:
            schemes = [x.scheme for x in item.additionalClassifications]
            schemes_inn_count = schemes.count(INN_SCHEME)
            if item.classification.id == CPV_PHARM_PRODUCTS and schemes_inn_count != 1:
                raise ValidationError(
                    "Item with classification.id={} have to contain exactly one additionalClassifications "
                    "with scheme={}".format(CPV_PHARM_PRODUCTS, INN_SCHEME)
                )
            if item.classification.id.startswith(CPV_PHARM_PRODUCTS[:3]) and schemes_inn_count > 1:
                raise ValidationError(
                    "Item with classification.id that starts with {} and contains additionalClassification "
                    "objects have to contain no more than one additionalClassifications "
                    "with scheme={}".format(CPV_PHARM_PRODUCTS[:3], INN_SCHEME)
                )


def _validate_accreditation_level(request, levels, name, action):
    if not request.check_accreditations(levels):
        request.errors.add(
            "url", "accreditation", "Broker Accreditation level does not permit {} {}".format(name, action)
        )
        request.errors.status = 403
        raise error_handler(request)


def _validate_accreditation_level_mode(request, mode, name, action):
    if mode is None and request.check_accreditations((ACCR_TEST,)):
        request.errors.add(
            "url", "mode", "Broker Accreditation level does not permit {} {}".format(name, action)
        )
        request.errors.status = 403
        raise error_handler(request)


def _validate_accreditation_level_owner(request, owner, location, name, action):
    if not check_user_accreditations(request, owner, (ACCR_EXIT,), default=True):
        request.errors.add(
            "url", "accreditation", "Owner Accreditation level does not permit {} {}".format(name, action)
        )
        request.errors.status = 403
        raise error_handler(request)


def _validate_accreditation_level_kind(request, levels, kind, name, action):
    if kind == "central":
        _validate_accreditation_level(request, levels, name, action)


def _validate_tender_first_revision_date(request, validation_date, message="Forbidden"):
    tender = request.validated["tender"]
    tender_creation_date = get_first_revision_date(tender, default=get_now())
    if tender_creation_date < validation_date:
        raise_operation_error(request, message)


def validate_doc_accreditation_level_mode(request, methodType, doc_type):
    data = request.validated["data"]
    mode = data.get("mode", None)
    _validate_accreditation_level_mode(request, mode, doc_type, "creation")
