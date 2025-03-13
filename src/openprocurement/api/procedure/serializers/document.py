from string import hexdigits
from typing import Any
from urllib.parse import parse_qs, urlparse

from openprocurement.api.constants import ROUTE_PREFIX
from openprocurement.api.context import get_request
from openprocurement.api.procedure.models.document import ConfidentialityType
from openprocurement.api.procedure.serializers.base import BaseSerializer
from openprocurement.api.utils import generate_docservice_url


def download_url_serialize(url, document):
    if not url or "?download=" not in url:
        return url
    doc_id = parse_qs(urlparse(url).query)["download"][-1]
    request = get_request()
    if not document.get("hash"):
        path = [i for i in urlparse(url).path.split("/") if len(i) == 32 and not set(i).difference(hexdigits)]
        return generate_docservice_url(request, doc_id, False, "{}/{}".format(path[0], path[-1]))
    return generate_docservice_url(request, doc_id, False)


#  WARNING, there is a
#  `@subscriber(BeforeRender)`
#  `def beforerender(event):`
#  in openprocurement.api
#  that works globally for all the requests and to documents like {"url": "/tenders/uid/blabla"}
#  adds host: {"url": "http://localhost/tenders/uid/blabla"}
#  TODO: move it to the Serializer


def url_to_absolute(url):
    if url.startswith("/"):
        request = get_request()
        result = f"{request.scheme}://{request.host}{ROUTE_PREFIX}{url}"
        return result


def confidential_url_serialize(url, document):
    # disabling download_url_serialize. TODO: Can be done for all the documents ?
    if document.get("confidentiality") == ConfidentialityType.BUYER_ONLY:
        return url_to_absolute(url)
    return download_url_serialize(url, document)


class DocumentSerializer(BaseSerializer):
    serializers = {
        "url": confidential_url_serialize,
    }

    def serialize_value(self, key: str, value: Any, **kwargs) -> Any:
        kwargs = kwargs.copy()
        if key == "url":
            kwargs["document"] = self.raw
        return super().serialize_value(key, value, **kwargs)
