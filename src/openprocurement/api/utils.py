from base64 import b64encode
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime
from functools import partial
from json import dumps
from time import time as ttime
from urllib.parse import urlencode, urlparse, urlunsplit
from uuid import uuid4

import requests
from ciso8601 import parse_datetime
from cornice.resource import view
from cornice.util import json_error
from dateorro import calc_datetime, calc_normalized_datetime, calc_working_datetime
from jsonpointer import JsonPointerException
from nacl.encoding import HexEncoder
from pymongo.errors import DuplicateKeyError, OperationFailure
from schematics.exceptions import (
    ModelConversionError,
    ModelValidationError,
    ValidationError,
)
from webob.multidict import NestedMultiDict

from openprocurement.api.constants import (
    DST_AWARE_PERIODS_FROM,
    GMDN_CPV_PREFIXES,
    JOURNAL_PREFIX,
    LOGGER,
    ROUTE_PREFIX,
    TZ,
    UA_ROAD_CPV_PREFIXES,
    WORKING_DAYS,
)
from openprocurement.api.context import get_local_cache
from openprocurement.api.database import MongodbResourceConflict
from openprocurement.api.events import ErrorDescriptorEvent

json_view = partial(view, renderer="simplejson")


def get_obj_by_id(request, collection_name: str, obj_id: str, raise_error: bool = True):
    if not obj_id:
        return
    collection = getattr(request.registry.mongodb, collection_name)
    obj = collection.get(obj_id)
    obj_name = collection_name[:-1]
    if obj is None and raise_error:
        request.errors.add("url", f"{obj_name}_id", "Not Found")
        request.errors.status = 404
        raise error_handler(request)
    elif obj is None:
        LOGGER.error(
            f"{obj_name.capitalize()} {obj_id} not found",
            extra=context_unpack(request, {"MESSAGE_ID": f"get_{obj_name}_by_id"}),
        )

    return obj


def get_plan_by_id(request, plan_id: str, raise_error: bool = True):
    return get_obj_by_id(request, "plans", plan_id, raise_error)


def get_tender_by_id(request, tender_id: str, raise_error: bool = True):
    return get_obj_by_id(request, "tenders", tender_id, raise_error)


def get_contract_by_id(request, contract_id: str, raise_error: bool = True):
    return get_obj_by_id(request, "contracts", contract_id, raise_error)


def get_framework_by_id(request, framework_id: str, raise_error: bool = True):
    return get_obj_by_id(request, "frameworks", framework_id, raise_error)


def get_submission_by_id(request, submission_id: str, raise_error: bool = True):
    return get_obj_by_id(request, "submissions", submission_id, raise_error)


def get_qualification_by_id(request, qualification_id: str, raise_error: bool = True):
    return get_obj_by_id(request, "qualifications", qualification_id, raise_error)


def get_agreement_by_id(request, agreement_id: str, raise_error: bool = True):
    return get_obj_by_id(request, "agreements", agreement_id, raise_error)


def request_init_object(request, obj_name, obj, obj_src=None):
    if obj is None:
        return
    if obj_src is None:
        obj_src = deepcopy(obj)
    request.validated[obj_name] = obj
    request.validated[f"{obj_name}_src"] = obj_src
    config_serializer = get_config_serializer(request, obj_name)
    if config_serializer:
        obj["config"] = config_serializer(obj.get("config", {})).data

        # TODO:
        #  maybe there is a better single place to do this
        #  or just delete it when we do not need it anymore

        # pylint: disable-next=import-outside-toplevel, cyclic-import
        from openprocurement.api.procedure.validation import (
            validate_restricted_object_action,
        )

        validate_restricted_object_action(request, obj_name, obj)
    return request.validated[obj_name]


def get_registry_object(registry, key, default=None):
    if not hasattr(registry, key):
        setattr(registry, key, default)
    return getattr(registry, key)


def register_config_serializer(config, obj_name, config_serializer):
    registry_object = get_registry_object(config.registry, "config_serializers", default={})
    registry_object[obj_name] = config_serializer


def get_config_serializer(request, obj_name):
    registry_object = get_registry_object(request.registry, "config_serializers", default={})
    return registry_object.get(obj_name)


def request_init_plan(request, plan, plan_src=None, raise_error=True):
    return request_init_object(
        request,
        "plan",
        plan,
        obj_src=plan_src,
    )


def request_init_tender(request, tender, tender_src=None, raise_error=True):
    return request_init_object(
        request,
        "tender",
        tender,
        obj_src=tender_src,
    )


def request_init_contract(request, contract, contract_src=None, raise_error=True):
    return request_init_object(
        request,
        "contract",
        contract,
        obj_src=contract_src,
    )


def request_init_framework(request, framework, framework_src=None, raise_error=True):
    return request_init_object(
        request,
        "framework",
        framework,
        obj_src=framework_src,
    )


def request_init_submission(request, submission, submission_src=None, raise_error=True):
    return request_init_object(
        request,
        "submission",
        submission,
        obj_src=submission_src,
    )


def request_init_qualification(request, qualification, qualification_src=None, raise_error=True):
    return request_init_object(
        request,
        "qualification",
        qualification,
        obj_src=qualification_src,
    )


def request_init_agreement(request, agreement, agreement_src=None, raise_error=True):
    return request_init_object(
        request,
        "agreement",
        agreement,
        obj_src=agreement_src,
    )


def request_init_transfer(request, transfer, transfer_src=None, raise_error=True):
    return request_init_object(
        request,
        "transfer",
        transfer,
        obj_src=transfer_src,
    )


def request_fetch_plan(request, plan_id, raise_error=True, force=False):
    if should_fetch_object(request, "plan", force=force):
        plan = get_submission_by_id(request, plan_id, raise_error=raise_error)
        request_init_plan(request, plan)


def request_fetch_tender(request, tender_id, raise_error=True, force=False):
    if should_fetch_object(request, "tender", force=force):
        tender = get_tender_by_id(request, tender_id, raise_error=raise_error)
        request_init_tender(request, tender)


def request_fetch_contract(request, contract_id, raise_error=True, force=False):
    if should_fetch_object(request, "contract", force=force):
        contract = get_contract_by_id(request, contract_id, raise_error=raise_error)
        request_init_contract(request, contract)


def request_fetch_framework(request, framework_id, raise_error=True, force=False):
    if should_fetch_object(request, "framework", force=force):
        framework = get_framework_by_id(request, framework_id, raise_error=raise_error)
        request_init_framework(request, framework)


def request_fetch_submission(request, submission_id, raise_error=True, force=False):
    if should_fetch_object(request, "submission", force=force):
        submission = get_submission_by_id(request, submission_id, raise_error=raise_error)
        request_init_submission(request, submission)


def request_fetch_qualification(request, qualification_id, raise_error=True, force=False):
    if should_fetch_object(request, "qualification", force=force):
        qualification = get_qualification_by_id(request, qualification_id, raise_error=raise_error)
        request_init_qualification(request, qualification)


def request_fetch_agreement(request, agreement_id, raise_error=True, force=False):
    if should_fetch_object(request, "agreement", force=force):
        agreement = get_agreement_by_id(request, agreement_id, raise_error=raise_error)
        request_init_agreement(request, agreement)


def should_fetch_object(request, obj_name, force=False):
    if obj_name not in request.validated or force is True:
        return True
    return False


def get_now():
    return datetime.now(TZ)


def set_parent(item, parent):
    if hasattr(item, "__parent__") and item.__parent__ is None:
        item.__parent__ = parent


def generate_id():
    return uuid4().hex


def generate_docservice_url(request, doc_id, temporary=True, prefix=None):
    signer = getattr(request.registry, "docservice_key", None)
    keyid = signer.verify_key.encode(encoder=HexEncoder)[:8].decode()

    parsed_url = urlparse(request.registry.docservice_url)
    query = {}
    if temporary:
        expires = int(ttime()) + 300  # EXPIRES
        mess = "{}\0{}".format(doc_id, expires)
        query["Expires"] = expires
    else:
        mess = doc_id
    if prefix:
        mess = "{}/{}".format(prefix, mess)
        query["Prefix"] = prefix
    query["Signature"] = b64encode(signer.sign(mess.encode()).signature)
    query["KeyID"] = keyid
    return urlunsplit(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            "/get/{}".format(doc_id),
            urlencode(query),
            "",
        )
    )


def error_handler(request, request_params=True):
    errors = request.errors
    params = {"ERROR_STATUS": errors.status}
    if request_params:
        params["ROLE"] = str(request.authenticated_role)
        if request.params:
            params["PARAMS"] = str(dict(request.params))
    if request.matchdict:
        for x, j in request.matchdict.items():
            params[x.upper()] = j
    request.registry.notify(ErrorDescriptorEvent(request, params))

    for item in errors:
        for key, value in item.items():
            if isinstance(value, bytes):
                item[key] = value.decode("utf-8")

    LOGGER.info(
        'Error on processing request "{}"'.format(dumps(errors, indent=4)),
        extra=context_unpack(request, {"MESSAGE_ID": "error_handler"}, params),
    )
    return json_error(request)


def raise_operation_error(request, message, status=403, location="body", name="data"):
    """
    This function mostly used in views validators to add access errors and
    raise exceptions if requested operation is forbidden.
    """
    request.errors.add(location, name, message)
    request.errors.status = status
    raise error_handler(request)


def update_file_content_type(request):  # XXX TODO
    pass


def request_params(request):
    try:
        params = NestedMultiDict(request.GET, request.POST)
    except UnicodeDecodeError:
        request.errors.add("body", "data", "could not decode params")
        request.errors.status = 422
        raise error_handler(request, False)
    except Exception as e:
        request.errors.add("body", str(e.__class__.__name__), str(e))
        request.errors.status = 422
        raise error_handler(request, False)
    return params


def forbidden(request):
    request.errors.add("url", "permission", "Forbidden")
    request.errors.status = 403
    return error_handler(request)


def precondition(request):
    request.errors.add("url", "precondition", "Precondition Failed")
    request.errors.status = 412
    return error_handler(request)


def update_logging_context(request, params):
    if not request.__dict__.get("logging_context"):
        request.logging_context = {}

    for x, j in params.items():
        request.logging_context[x.upper()] = j


def context_unpack(request, msg, params=None):
    if params:
        update_logging_context(request, params)
    logging_context = request.logging_context
    journal_context = msg
    for key, value in logging_context.items():
        journal_context[JOURNAL_PREFIX + key] = value
    return journal_context


def fix_url(item, app_url):
    if isinstance(item, list):
        [fix_url(i, app_url) for i in item if isinstance(i, dict) or isinstance(i, list)]
    elif isinstance(item, dict):
        if "format" in item and "url" in item and "?download=" in item["url"]:
            path = item["url"] if item["url"].startswith("/") else "/" + "/".join(item["url"].split("/")[5:])
            item["url"] = app_url + ROUTE_PREFIX + path
            return
        [fix_url(item[i], app_url) for i in item if isinstance(item[i], dict) or isinstance(item[i], list)]


def get_first_revision_date(schematics_document, default=None):
    revisions = schematics_document.get("revisions") if schematics_document else None
    return parse_datetime(revisions[0]["date"]) if revisions else default


def is_ua_road_classification(classification_id):
    return classification_id[:4] in UA_ROAD_CPV_PREFIXES


def is_gmdn_classification(classification_id):
    return classification_id[:4] in GMDN_CPV_PREFIXES


@contextmanager
def handle_data_exceptions(request):
    try:
        yield
    except (ModelValidationError, ModelConversionError) as e:
        if isinstance(e.messages, dict):
            for key, value in e.messages.items():
                request.errors.add("body", key, value)
        elif isinstance(e.messages, list):
            for value in e.messages:
                request.errors.add("body", "data", value)
        request.errors.status = 422
        raise error_handler(request)
    except ValueError as e:
        request.errors.add("body", "data", str(e))
        request.errors.status = 422
        raise error_handler(request)
    except JsonPointerException as e:
        request.errors.add("body", "data", str(e))
        request.errors.status = 422
        raise error_handler(request)


@contextmanager
def handle_store_exceptions(request, raise_error_handler=False):
    try:
        yield
    except ModelValidationError as e:
        for i in e.messages:
            request.errors.add("body", i, e.messages[i])
        request.errors.status = 422
    except DuplicateKeyError:  # pragma: no cover
        request.errors.add("body", "data", "Document already exists")
        request.errors.status = 409
    except MongodbResourceConflict as e:  # pragma: no cover
        request.errors.add("body", "data", str(e))
        request.errors.status = 409
    except OperationFailure as e:
        LOGGER.warning(e.details)
        request.errors.add("body", "data", "Conflict while writing document. Please, retry.")
        request.errors.status = 409
    except Exception as e:  # pragma: no cover
        LOGGER.exception(e)
        request.errors.add("body", "data", str(e))
    if request.errors and raise_error_handler:
        raise error_handler(request)


def get_currency_rates(request):
    kwargs = {}
    proxy_address = request.registry.settings.get("proxy_address")
    if proxy_address:
        kwargs.update(proxies={"http": proxy_address, "https": proxy_address})
    base_url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?date={}&json".format(
        get_now().strftime("%Y%m%d")
    )
    try:
        resp = requests.get(base_url, **kwargs)
    except requests.exceptions.RequestException as e:
        raise raise_operation_error(
            request,
            "Error while getting data from bank.gov.ua: {}".format(e),
            status=409,
        )
    try:
        return resp.json()
    except ValueError:
        raise raise_operation_error(request, "Failure of decoding data from bank.gov.ua", status=409)


def get_uah_amount_from_value(request, value, logging_params):
    amount = float(value["amount"])
    currency = value["currency"]
    if currency != "UAH":
        for row in request.currency_rates:
            if row["cc"] == currency:
                currency_rate = row["rate"]
                break
        else:
            raise raise_operation_error(
                request,
                "Couldn't find currency {} on bank.gov.ua".format(currency),
                status=422,
            )

        amount *= currency_rate
        LOGGER.info(
            "Converting {} {} into {} UAH using rate {}".format(
                value["amount"], value["currency"], amount, currency_rate
            ),
            extra=context_unpack(request, {"MESSAGE_ID": "complaint_exchange_rate"}, logging_params),
        )
    return amount


def json_body(request):
    return request.json_body


def get_change_class(poly_model, data, _validation=False):
    rationale_type = data.get("rationaleType")
    rationale_type_class_name_mapping = {
        "taxRate": "ChangeTaxRate",
        "itemPriceVariation": "ChangeItemPriceVariation",
        "partyWithdrawal": "ChangePartyWithdrawal",
        "thirdParty": "ChangeThirdParty",
    }
    _class_name = rationale_type_class_name_mapping.get(rationale_type)
    if not _class_name:
        if _validation:
            return None
        raise ValidationError("Input for polymorphic field did not match any model")

    _change_class = [model_class for model_class in poly_model.model_classes if model_class.__name__ == _class_name][0]
    return _change_class


def requested_fields_changes(request, fieldnames):
    changed_fields = request.validated["json_data"].keys()
    return set(fieldnames) & set(changed_fields)


def get_child_items(parent: dict, item_field: str, item_id: str) -> list:
    return [i for i in parent.get(item_field, []) if i.get("id") == item_id]


def delete_nones(data: dict):
    for k, v in tuple(data.items()):
        if v is None:
            del data[k]


def get_catalogue_object(request, uri: str, obj_id: str, valid_statuses: tuple = None) -> dict:
    catalog_api_host = request.registry.catalog_api_host
    obj_name = uri.split("/")[-1]

    cache_key = f"get_catalogue_object_{uri}_{obj_id}"
    cache = get_local_cache()
    data = cache.get(cache_key)

    if not data:
        try:
            resp = requests.get(f"{catalog_api_host}/api/{uri}/{obj_id}")
        except requests.exceptions.RequestException as e:
            LOGGER.warning(f"Error while getting data from ProZorro e-Catalogues. Details: {e}")
            raise raise_operation_error(
                request,
                "Error while getting data from ProZorro e-Catalogues: Connection closed. Try again later",
                status=502,
            )
        if resp.status_code == 404:
            raise_operation_error(
                request,
                f"{obj_name.capitalize()} {obj_id} not found in catalouges.",
                status=404,
            )
        elif resp.status_code != 200:
            raise_operation_error(
                request,
                f"Fail getting {obj_name} {obj_id}: {resp.status_code} {resp.text}.",
                status=resp.status_code,
            )

        data = cache[cache_key] = resp.json().get("data", {})

    if valid_statuses:
        if data.get("status", "active") not in valid_statuses:
            raise_operation_error(
                request,
                f"{obj_name.capitalize()} {obj_id}: {data['status']} not in {valid_statuses}",
                status=422,
            )

    return data


def get_tender_profile(request, profile_id: str, validate_status: tuple = None) -> dict:
    return get_catalogue_object(request, "profiles", profile_id, validate_status)


def get_tender_category(request, category_id: str, validate_status: tuple = None) -> dict:
    return get_catalogue_object(request, "categories", category_id, validate_status)


def get_tender_product(request, product_id: str, validate_status: tuple = None) -> dict:
    return get_catalogue_object(request, "products", product_id, validate_status)


def calculate_normalized_date(date_obj, ceil=False):
    result_date_obj = calc_normalized_datetime(date_obj, ceil=ceil)
    if date_obj > DST_AWARE_PERIODS_FROM:
        result_date_obj = TZ.localize(result_date_obj.replace(tzinfo=None))
    return result_date_obj


def calculate_date(date_obj, timedelta_obj, working_days=False, calendar=WORKING_DAYS):
    if working_days:
        result_date_obj = calc_working_datetime(date_obj, timedelta_obj, calendar=calendar)
    else:
        result_date_obj = calc_datetime(date_obj, timedelta_obj)
    if date_obj > DST_AWARE_PERIODS_FROM:
        result_date_obj = TZ.localize(result_date_obj.replace(tzinfo=None))
    return result_date_obj


def calculate_full_date(date_obj, timedelta_obj, working_days=False, calendar=WORKING_DAYS, ceil=False):
    start_obj = calculate_normalized_date(date_obj, ceil=ceil)
    return calculate_date(start_obj, timedelta_obj, working_days=working_days, calendar=calendar)


def is_boolean(value):
    if isinstance(value, bool):
        return True

    if isinstance(value, str):
        value = value.strip().lower()
        if value in ("true", "1"):
            return True
        elif value in ("false", "0"):
            return False

    return False
