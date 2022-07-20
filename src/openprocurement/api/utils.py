# -*- coding: utf-8 -*-
import re
from contextlib import contextmanager
from decimal import Decimal

from jsonpointer import JsonPointerException
from pymongo.errors import DuplicateKeyError
from six import b
import pytz
from logging import getLogger
from datetime import datetime, timezone
from base64 import b64encode, b64decode
from cornice.resource import resource, view
from email.header import decode_header
from functools import partial

from ciso8601 import parse_datetime
from jsonpatch import make_patch, apply_patch
from schematics.types import StringType, BaseType
from schematics.models import Model as SchematicsModel

from openprocurement.api.traversal import factory
from rfc6266 import build_header
from hashlib import sha512
from time import time as ttime
from urllib.parse import urlparse, urlunsplit, parse_qsl, quote, unquote, urlencode
from nacl.encoding import HexEncoder
from nacl.exceptions import BadSignatureError
from uuid import uuid4
from webob.multidict import NestedMultiDict
from binascii import hexlify, unhexlify
from binascii import Error as BinasciiError
from Crypto.Cipher import AES
from cornice.util import json_error
from json import dumps

from schematics.exceptions import ValidationError, ModelValidationError, ModelConversionError
from openprocurement.api.events import ErrorDescriptorEvent
from openprocurement.api.constants import (
    LOGGER,
    JOURNAL_PREFIX,
    ADDITIONAL_CLASSIFICATIONS_SCHEMES,
    DOCUMENT_BLACKLISTED_FIELDS,
    DOCUMENT_WHITELISTED_FIELDS,
    ROUTE_PREFIX,
    TZ,
    SESSION,
    GMDN_CPV_PREFIXES,
    UA_ROAD_CPV_PREFIXES,
)
from openprocurement.api.database import MongodbResourceConflict
from openprocurement.api.interfaces import IOPContent
from openprocurement.api.interfaces import IContentConfigurator
import requests
import decimal
import json

json_view = partial(view, renderer="simplejson")

ACCELERATOR_RE = re.compile(".accelerator=(?P<accelerator>\d+)")


DEFAULT_PAGE = 1
DEFAULT_LIMIT = 100
DEFAULT_DESCENDING = False


def validate_dkpp(items, *args):
    if items and not any([i.scheme in ADDITIONAL_CLASSIFICATIONS_SCHEMES for i in items]):
        raise ValidationError(
            "One of additional classifications should be one of [{0}].".format(
                ", ".join(ADDITIONAL_CLASSIFICATIONS_SCHEMES)
            )
        )


def get_now():
    return datetime.now(TZ)


def request_get_now(request):
    return get_now()


def set_parent(item, parent):
    if hasattr(item, "__parent__") and item.__parent__ is None:
        item.__parent__ = parent


def get_root(item):
    """ traverse back to root op content object (plan, tender, contract, etc.)
    """
    while not IOPContent.providedBy(item):
        item = item.__parent__
    return item


def get_particular_parent(item, model):
    """ traverse back to particular parent
    """
    while not isinstance(item, model):
        item = item.__parent__
    return item


def get_particular_parent_by_namespace(item, model_namespace):
    """ traverse back to particular parent
    """
    while not item._options.namespace == model_namespace:
        item = item.__parent__
    return item

def generate_id():
    return uuid4().hex


def get_filename(data):
    try:
        pairs = decode_header(data.filename)
    except Exception:
        pairs = None
    if not pairs:
        return data.filename
    header = pairs[0]
    if header[1]:
        return header[0].decode(header[1])
    else:
        return header[0]


def get_schematics_document(model):
    while isinstance(model.__parent__, SchematicsModel):
        model = model.__parent__
    return model


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
    return urlunsplit((parsed_url.scheme, parsed_url.netloc, "/get/{}".format(doc_id), urlencode(query), ""))


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
                item[key] = value.decode('utf-8')

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


def upload_file(request):
    if "data" in request.validated and request.validated["data"]:
        return upload_file_json(request)
    return upload_file_direct(request)


def upload_files(request, container="documents"):
    bulk_documents = request.validated.get("document_bulk")
    if bulk_documents:
        for document in bulk_documents:
            yield upload_file_data(request, document, None)
    else:
        yield upload_file(request)


def upload_file_json(request):
    document = request.validated["document"]
    prev_documents = request.validated.get("documents")
    return upload_file_data(request, document, prev_documents)


def upload_file_data(request, document, prev_documents):
    first_document = prev_documents[-1] if prev_documents else None
    check_document(request, document)
    if first_document:
        update_new_document_version(request, document, first_document)
    document_route = request.matched_route.name.replace("collection_", "")
    document = update_document_url(request, document, document_route, {})
    return document


def upload_file_direct(request):
    prev_documents = request.validated.get("documents")
    first_document = prev_documents[-1] if prev_documents else None
    if request.content_type == "multipart/form-data":
        data = request.validated["file"]
        filename = get_filename(data)
        content_type = data.type
        in_file = data.file
    else:
        filename = first_document.title
        content_type = request.content_type
        in_file = request.body_file
    if hasattr(request.context, "documents"):
        # upload new document
        model = type(request.context).documents.model_class
    else:
        # update document
        model = type(request.context)
    document = model({"title": filename, "format": content_type})
    document.__parent__ = request.context
    if "document_id" in request.validated:
        document.id = request.validated["document_id"]
    if first_document:
        update_new_document_direct_version(document, first_document)
    if request.registry.docservice_url:
        key = upload_file_to_docservice(request, document, in_file, filename, content_type)
    else:
        key = upload_file_to_attachments(document, in_file, request)
    document_route = request.matched_route.name.replace("collection_", "")
    document_path = request.current_route_path(
        _route_name=document_route, document_id=document.id, _query={"download": key}
    )
    document.url = "/" + "/".join(document_path.split("/")[3:])
    update_logging_context(request, {"file_size": in_file.tell()})
    return document


def upload_file_to_docservice(request, document, in_file, filename, content_type):
    parsed_url = urlparse(request.registry.docservice_url)
    url = request.registry.docservice_upload_url or urlunsplit(
        (parsed_url.scheme, parsed_url.netloc, "/upload", "", "")
    )
    files = {"file": (filename, in_file, content_type)}
    doc_url = None
    index = 10
    while index:
        try:
            r = SESSION.post(
                url,
                files=files,
                headers={"X-Client-Request-ID": request.environ.get("REQUEST_ID", "")},
                auth=(request.registry.docservice_username, request.registry.docservice_password),
            )
            json_data = r.json()
        except Exception as e:
            LOGGER.warning(
                "Raised exception '{}' on uploading document to document service': {}.".format(type(e), e),
                extra=context_unpack(
                    request, {"MESSAGE_ID": "document_service_exception"}, {"file_size": in_file.tell()}
                ),
            )
        else:
            if r.status_code == 200 and json_data.get("data", {}).get("url"):
                doc_url = json_data["data"]["url"]
                doc_hash = json_data["data"]["hash"]
                break
            else:
                LOGGER.warning(
                    "Error {} on uploading document to document service '{}': {}".format(
                        r.status_code, url, r.text
                    ),
                    extra=context_unpack(
                        request,
                        {"MESSAGE_ID": "document_service_error"},
                        {"ERROR_STATUS": r.status_code, "file_size": in_file.tell()},
                    ),
                )
        in_file.seek(0)
        index -= 1
    else:
        request.errors.add("body", "body", "Can't upload document to document service.")
        request.errors.status = 422
        raise error_handler(request)
    document.hash = doc_hash
    key = urlparse(doc_url).path.split("/")[-1]
    return key


def upload_file_to_attachments(document, in_file, request):
    key = generate_id()
    filename = "{}_{}".format(document.id, key)
    request.validated["db_doc"]["_attachments"][filename] = {
        "content_type": document.format,
        "data": b64encode(in_file.read()).decode('utf-8'),
    }
    return key


def update_new_document_version(
    request, document, first_document,
    blacklisted_fields=DOCUMENT_BLACKLISTED_FIELDS,
    whitelisted_fields=DOCUMENT_WHITELISTED_FIELDS
):
    json_data = request.validated["json_data"]
    if isinstance(json_data, list):
        for json_item in json_data:
            if json_item["id"] == first_document["id"]:
                json_document = json_item
                break
        else:
            raise ValueError
    else:
        json_document = json_data
    for attr_name in type(first_document)._fields:
        if attr_name in whitelisted_fields:
            setattr(document, attr_name, getattr(first_document, attr_name))
        elif attr_name not in blacklisted_fields and attr_name not in json_document:
            setattr(document, attr_name, getattr(first_document, attr_name))


def update_new_document_direct_version(
    document, first_document,
    blacklisted_fields=DOCUMENT_BLACKLISTED_FIELDS,
):
    for attr_name in type(first_document)._fields:
        if attr_name not in blacklisted_fields:
            setattr(document, attr_name, getattr(first_document, attr_name))


def update_file_content_type(request):  # XXX TODO
    pass


def get_file(request):
    db_doc_id = request.validated["db_doc"].id
    key = request.params.get("download")
    if not any([key in i.url for i in request.validated["documents"]]):
        request.errors.add("url", "download", "Not Found")
        request.errors.status = 404
        return
    return get_file_docservice(request, db_doc_id, key)


def get_file_docservice(request, db_doc_id, key):
    document = [i for i in request.validated["documents"] if key in i.url][-1]
    if "Signature=" in document.url and "KeyID" in document.url:
        url = document.url
    else:
        if "download=" not in document.url:
            key = urlparse(document.url).path.replace("/get/", "")
        if not document.hash:
            url = generate_docservice_url(request, key, prefix="{}/{}".format(db_doc_id, document.id))
        else:
            url = generate_docservice_url(request, key)
    request.response.content_type = document.format
    request.response.content_disposition = build_header(
        document.title, filename_compat=quote(document.title.encode("utf-8"))
    ).decode("utf-8")
    request.response.status = "302 Moved Temporarily"
    request.response.location = url
    return url


def prepare_patch(changes, orig, patch, basepath=""):
    if isinstance(patch, dict):
        for i in patch:
            if i in orig:
                prepare_patch(changes, orig[i], patch[i], "{}/{}".format(basepath, i))
            else:
                changes.append({"op": "add", "path": "{}/{}".format(basepath, i), "value": patch[i]})
    elif isinstance(patch, list):
        if len(patch) < len(orig):
            for i in reversed(list(range(len(patch), len(orig)))):
                changes.append({"op": "remove", "path": "{}/{}".format(basepath, i)})
        for i, j in enumerate(patch):
            if len(orig) > i:
                prepare_patch(changes, orig[i], patch[i], "{}/{}".format(basepath, i))
            else:
                changes.append({"op": "add", "path": "{}/{}".format(basepath, i), "value": j})
    else:
        for x in make_patch(orig, patch).patch:
            x["path"] = "{}{}".format(basepath, x["path"])
            changes.append(x)


def apply_data_patch(item, changes):
    patch_changes = []
    prepare_patch(patch_changes, item, changes)
    if not patch_changes:
        return {}
    return apply_patch(item, patch_changes)


def get_revision_changes(dst, src):
    return make_patch(dst, src).patch


def set_ownership(item, request):
    if not item.get("owner"):
        item.owner = request.authenticated_userid
    item.owner_token = generate_id()
    access = {"token": item.owner_token}
    if isinstance(getattr(type(item), "transfer_token", None), StringType):
        transfer = generate_id()
        item.transfer_token = sha512(transfer.encode("utf-8")).hexdigest()
        access["transfer"] = transfer
    return access


def check_document(request, document):
    url = document.url
    parsed_url = urlparse(url)
    parsed_query = dict(parse_qsl(parsed_url.query))
    if (
        not (
            url.startswith(request.registry.docservice_url)
            or request.registry.dep_docservice_url and url.startswith(request.registry.dep_docservice_url)
        )
        or len(parsed_url.path.split("/")) != 3
        or {"Signature", "KeyID"} != set(parsed_query)
    ):
        request.errors.add("body", "url", "Can add document only from document service.")
        request.errors.status = 403
        raise error_handler(request)
    if not document.hash:
        request.errors.add("body", "hash", "This field is required.")
        request.errors.status = 422
        raise error_handler(request)
    keyid = parsed_query["KeyID"]
    if keyid not in request.registry.keyring:
        request.errors.add("body", "url", "Document url expired.")
        request.errors.status = 422
        raise error_handler(request)
    dockey = request.registry.keyring[keyid]
    signature = parsed_query["Signature"]
    key = urlparse(url).path.split("/")[-1]
    try:
        signature = b64decode(unquote(signature))
    except BinasciiError:
        request.errors.add("body", "url", "Document url signature invalid.")
        request.errors.status = 422
        raise error_handler(request)
    mess = "{}\0{}".format(key, document.hash.split(":", 1)[-1])
    try:
        if mess.encode() != dockey.verify(signature + mess.encode("utf-8")):
            raise BadSignatureError
    except BadSignatureError:
        request.errors.add("body", "url", "Document url invalid.")
        request.errors.status = 422
        raise error_handler(request)


def update_document_url(request, document, document_route, route_kwargs=None):
    route_kwargs = route_kwargs or {}
    key = urlparse(document.url).path.split("/")[-1]
    route_kwargs.update({"_route_name": document_route, "document_id": document.id, "_query": {"download": key}})
    document_path = request.current_route_path(**route_kwargs)
    document.url = "/" + "/".join(document_path.split("/")[3:])
    return document


def check_document_batch(request, document, document_container, route_kwargs=None, route_prefix=None):
    check_document(request, document)
    document_route = request.matched_route.name.replace("collection_", "")
    # Following piece of code was written by leits, so no one knows how it works
    # and why =)
    # To redefine document_route to get appropriate real document route when bid
    # is created with documents? I hope so :)
    if "Documents" not in document_route:
        if document_container != "body":
            route_end = document_container.lower().rsplit("documents")[0] + " documents"
        else:
            route_end = "documents"
        specified_document_route_end = route_end.lstrip().title()
        document_route = " ".join([document_route[:-1], specified_document_route_end])
        if route_prefix:
            document_route = ":".join([route_prefix, document_route])
    return update_document_url(request, document, document_route, route_kwargs)


def upload_objects_documents(request, obj, document_container='body', route_kwargs=None, route_prefix=None):
    if request.registry.docservice_url:
        documents = getattr(obj, 'documents', []) if not isinstance(obj, list) else obj
        for document in documents:
            check_document_batch(request, document, document_container, route_kwargs, route_prefix)


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


opresource = partial(resource, error_handler=error_handler, factory=factory)


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


def get_content_configurator(request):
    content_type = request.path[len(ROUTE_PREFIX) + 1 :].split("/")[0][:-1]
    if hasattr(request, content_type):  # content is constructed
        context = getattr(request, content_type)
        return request.registry.queryMultiAdapter((context, request), IContentConfigurator)


def fix_url(item, app_url):
    if isinstance(item, list):
        [fix_url(i, app_url) for i in item if isinstance(i, dict) or isinstance(i, list)]
    elif isinstance(item, dict):
        if "format" in item and "url" in item and "?download=" in item["url"]:
            path = item["url"] if item["url"].startswith("/") else "/" + "/".join(item["url"].split("/")[5:])
            item["url"] = app_url + ROUTE_PREFIX + path
            return
        [fix_url(item[i], app_url) for i in item if isinstance(item[i], dict) or isinstance(item[i], list)]


def encrypt(uuid, name, key):
    iv = "{:^{}.{}}".format(name, AES.block_size, AES.block_size)
    text = "{:^{}}".format(key, AES.block_size)
    return hexlify(AES.new(b(uuid), AES.MODE_CBC, b(iv)).encrypt(b(text)))


def decrypt(uuid, name, key):
    iv = "{:^{}.{}}".format(name, AES.block_size, AES.block_size)
    try:
        text = AES.new(b(uuid), AES.MODE_CBC, b(iv)).decrypt(unhexlify(b(key))).strip()
    except:
        text = ""
    return text


def set_modetest_titles(item):
    if not item.title or "[ТЕСТУВАННЯ]" not in item.title:
        item.title = "[ТЕСТУВАННЯ] {}".format(item.title or "")
    if not item.title_en or "[TESTING]" not in item.title_en:
        item.title_en = "[TESTING] {}".format(item.title_en or "")
    if not item.title_ru or "[ТЕСТИРОВАНИЕ]" not in item.title_ru:
        item.title_ru = "[ТЕСТИРОВАНИЕ] {}".format(item.title_ru or "")


def get_first_revision_date(schematics_document, default=None):
    revisions = schematics_document.get("revisions") if schematics_document else None
    return parse_datetime(revisions[0]["date"]) if revisions else default


def is_ua_road_classification(classification_id):
    return classification_id[:4] in UA_ROAD_CPV_PREFIXES


def is_gmdn_classification(classification_id):
    return classification_id[:4] in GMDN_CPV_PREFIXES


def to_decimal(value):
    """
    Convert other to Decimal.
    """
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int) or isinstance(value, str):
        return Decimal(value)
    if isinstance(value, float):
        return Decimal(repr(value))

    raise TypeError("Unable to convert %s to Decimal" % value)


def append_revision(request, obj, patch):
    from openprocurement.api.models import Revision
    revision_data = {
        "author": request.authenticated_userid,
        "changes": patch,
        "rev": obj.rev
    }
    obj.revisions.append(Revision(revision_data).serialize())
    return obj.revisions


@contextmanager
def handle_data_exceptions(request):
    try:
        yield
    except (ModelValidationError, ModelConversionError) as e:
        if isinstance(e.messages, dict):
            for key, value in e.messages.items():
                request.errors.add("body", key, value)
        elif isinstance(e.messages, list):
            for i, value in enumerate(e.messages):
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
def handle_store_exceptions(request):
    try:
        yield
    except ModelValidationError as e:
        for i in e.messages:
            request.errors.add("body", i, e.messages[i])
        request.errors.status = 422
    except MongodbResourceConflict as e:  # pragma: no cover
        request.errors.add("body", "data", str(e))
        request.errors.status = 409
    except DuplicateKeyError as e:  # pragma: no cover
        request.errors.add("body", "data", "Document already exists")
        request.errors.status = 409
    except Exception as e:  # pragma: no cover
        LOGGER.exception(e)
        request.errors.add("body", "data", str(e))


def get_currency_rates(request):
    kwargs = {}
    proxy_address = request.registry.settings.get("proxy_address")
    if proxy_address:
        kwargs.update(proxies={"http": proxy_address, "https": proxy_address})
    base_url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?date={}&json".format(
        get_now().strftime('%Y%m%d')
    )
    try:
        resp = requests.get(base_url, **kwargs)
    except requests.exceptions.RequestException as e:
        raise raise_operation_error(
            request,
            "Error while getting data from bank.gov.ua: {}".format(e),
            status=409
        )
    try:
        return resp.json()
    except ValueError:
        raise raise_operation_error(
            request,
            "Failure of decoding data from bank.gov.ua",
            status=409
        )


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
                status=422
            )

        amount *= currency_rate
        LOGGER.info(
            "Converting {} {} into {} UAH using rate {}".format(
                value["amount"], value["currency"],
                amount, currency_rate
            ),
            extra=context_unpack(
                request, {"MESSAGE_ID": "complaint_exchange_rate"}, logging_params
            ),
        )
    return amount


def is_new_created(data):
    """
    Check if data['_rev'] is None then tender was created just now
    """
    return data["_rev"] is None


def json_body(request):
    return request.json_body


def parse_date(value, default_timezone=pytz.utc):
    date = parse_datetime(value)
    if not date.tzinfo:
        date = default_timezone.localize(date)
    return date


def get_change_class(poly_model, data, _validation=False):
    rationale_type = data.get("rationaleType")
    rationale_type_class_name_mapping = {
        "taxRate": "ChangeTaxRate",
        "itemPriceVariation": "ChangeItemPriceVariation",
        "partyWithdrawal": "ChangePartyWithdrawal",
        "thirdParty": "ChangeThirdParty"
    }
    _class_name = rationale_type_class_name_mapping.get(rationale_type)
    if not _class_name:
        if _validation:
            return None
        raise ValidationError("Input for polymorphic field did not match any model")

    _change_class = [model_class for model_class in poly_model.model_classes if model_class.__name__ == _class_name][0]
    return _change_class


def get_criterion_requirement(tender, requirement_id):
    for criteria in tender.criteria:
        for group in criteria.requirementGroups:
            for req in group.requirements:
                if req.id == requirement_id:
                    return criteria
    return None


def required_field_from_date(date):
    def decorator(function):
        def wrapper(*args, **kwargs):
            data, value = args[1:]
            try:
                root = get_root(data.get("__parent__", {}))
            except AttributeError:
                pass
            else:
                is_valid_date = get_first_revision_date(root, default=get_now()) >= date
                if is_valid_date and not value:
                    raise ValidationError(BaseType.MESSAGES["required"])
            function(*args, **kwargs)
        return wrapper
    return decorator
