# -*- coding: utf-8 -*-
from base64 import b64encode, b64decode
from urllib.parse import urlparse, urlunsplit, parse_qsl, quote, unquote, urlencode
from nacl.exceptions import BadSignatureError
from binascii import Error as BinasciiError
from openprocurement.api.utils import error_handler, generate_docservice_url, build_header


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


def update_document_url(request, document, document_route, route_kwargs=None):
    route_kwargs = route_kwargs or {}
    key = urlparse(document["url"]).path.split("/")[-1]
    route_kwargs.update({"_route_name": document_route, "document_id": document["id"], "_query": {"download": key}})
    document_path = request.current_route_path(**route_kwargs)
    document["url"] = "/" + "/".join(document_path.split("/")[3:])
    return document


def check_document(request, document):
    url = document["url"]
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
    if not document.get("hash"):  # Model validation not in the model, nice
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
    mess = "{}\0{}".format(key, document["hash"].split(":", 1)[-1])
    try:
        if mess.encode() != dockey.verify(signature + mess.encode("utf-8")):
            raise BadSignatureError
    except BadSignatureError:
        request.errors.add("body", "url", "Document url invalid.")
        request.errors.status = 422
        raise error_handler(request)


# downloading files
def get_file(request):
    db_doc_id = request.validated["tender"]["_id"]
    key = request.params.get("download")
    if not any(key in i["url"] for i in request.validated["documents"]):
        request.errors.add("url", "download", "Not Found")
        request.errors.status = 404
        return
    return get_file_docservice(request, db_doc_id, key)


def get_file_docservice(request, db_doc_id, key):
    document = request.validated["document"]
    document_url = document["url"]
    if "Signature=" in document_url and "KeyID" in document_url:
        url = document_url
    else:
        if "download=" not in document_url:
            key = urlparse(document_url).path.replace("/get/", "")
        if not document.get("hash"):
            url = generate_docservice_url(request, key, prefix="{}/{}".format(db_doc_id, document["id"]))
        else:
            url = generate_docservice_url(request, key)
    request.response.content_type = document["format"]
    request.response.content_disposition = build_header(
        document["title"], filename_compat=quote(document["title"].encode("utf-8"))
    ).decode("utf-8")
    request.response.status = "302 Moved Temporarily"
    request.response.location = url
    return url
