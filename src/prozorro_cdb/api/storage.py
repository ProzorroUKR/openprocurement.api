from base64 import b64decode, b64encode
from binascii import Error as BinasciiError
from time import time
from typing import Iterable, Tuple, TypeVar
from urllib.parse import parse_qsl, quote, unquote, urlencode, urlparse
from uuid import uuid4

from aiohttp.web import HTTPForbidden, HTTPFound, HTTPUnprocessableEntity
from nacl.encoding import HexEncoder
from nacl.exceptions import BadSignatureError

from openprocurement.api.rfc6266 import build_header
from prozorro_cdb.api.context import get_request_async
from prozorro_cdb.api.database.schema.document import Document
from prozorro_cdb.api.handlers.schema.document import PostDocument
from prozorro_cdb.api.settings import DocStorageConfig

DocumentDataT = TypeVar("DocumentDataT", bound=PostDocument)


def upload_documents(documents: list[DocumentDataT], current_url: str) -> Iterable[Tuple[str, DocumentDataT]]:
    doc_config = get_request_async().app.doc_storage_config
    for document in documents:
        check_document(doc_config, document)

        doc_id = uuid4().hex
        key = urlparse(str(document.url)).path.split("/")[-1]
        yield doc_id, document.model_copy(update=dict(url=f"{current_url}/documents/{doc_id}?download={key}"))


def check_document(doc_config: DocStorageConfig, document: DocumentDataT):
    url = str(document.url)
    parsed_url = urlparse(url)
    parsed_query = dict(parse_qsl(parsed_url.query))
    if (
        not (
            url.startswith(doc_config.service_url)
            or doc_config.dep_service_url
            and url.startswith(doc_config.dep_service_url)
        )
        or len(parsed_url.path.split("/")) != 3
        or {"Signature", "KeyID"} != set(parsed_query)
    ):
        raise HTTPForbidden(text="Can add document only from document service.")

    if not document.hash:  # Not empty string check now TODO: hash validation for model
        raise HTTPUnprocessableEntity(text="This field is required.")

    keyid = parsed_query["KeyID"]
    if keyid not in doc_config.keyring:
        raise HTTPUnprocessableEntity(text="Document url expired.")

    signature_str = parsed_query["Signature"]
    key = urlparse(url).path.split("/")[-1]
    try:
        signature: bytes = b64decode(unquote(signature_str))
    except BinasciiError:
        raise HTTPUnprocessableEntity(text="Document url signature invalid.")

    doc_key = doc_config.keyring[keyid]
    mess = "{}\0{}".format(key, document.hash.split(":", 1)[-1])
    try:
        if mess.encode() != doc_key.verify(signature + mess.encode("utf-8")):
            raise BadSignatureError
    except BadSignatureError:
        raise HTTPUnprocessableEntity(text="Document url invalid.")


def generate_doc_service_url(config: DocStorageConfig, doc_id, temporary=True, prefix=None):
    signer = config.service_key
    keyid = config.service_key.verify_key.encode(encoder=HexEncoder)[:8].decode()

    query = {}
    if temporary:
        expires = int(time()) + 300  # EXPIRES
        mess = "{}\0{}".format(doc_id, expires)
        query["Expires"] = expires
    else:
        mess = doc_id
    if prefix:
        mess = "{}/{}".format(prefix, mess)
        query["Prefix"] = prefix
    query["Signature"] = b64encode(signer.sign(mess.encode()).signature)
    query["KeyID"] = keyid
    return f"{config.service_url}/{doc_id}?{urlencode(query)}"


def download_file(document: Document, doc_id) -> HTTPFound:
    config = get_request_async().app.doc_storage_config

    url = generate_doc_service_url(config, doc_id)

    response = HTTPFound(location=url)
    response.content_type = document.format
    response.headers["Content-Disposition"] = build_header(
        document.title, filename_compat=quote(document.title.encode("utf-8"))
    ).decode("utf-8")
    return response
