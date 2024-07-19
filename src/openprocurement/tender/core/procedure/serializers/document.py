from string import hexdigits
from urllib.parse import parse_qs, urlparse

from openprocurement.api.constants import ROUTE_PREFIX
from openprocurement.api.procedure.serializers.base import BaseSerializer
from openprocurement.api.procedure.utils import is_item_owner
from openprocurement.api.utils import generate_docservice_url
from openprocurement.contracting.core.procedure.utils import is_tender_owner
from openprocurement.tender.core.procedure.context import get_request


def download_url_serialize(s, url):
    if not url or "?download=" not in url:
        return url
    doc_id = parse_qs(urlparse(url).query)["download"][-1]
    request = get_request()
    # WTF is this ????
    # parents = []
    # if "status" in parents[0] and parents[0].status in type(parents[0])._options.roles:
    #     role = parents[0].status
    #     for index, obj in enumerate(parents):
    #         if obj.id != url.split("/")[(index - len(parents)) * 2 - 1]:
    #             break
    #         field = url.split("/")[(index - len(parents)) * 2]
    #         if "_" in field:
    #             field = field[0] + field.title().replace("_", "")[1:]
    #         roles = type(obj)._options.roles
    #         if roles[role if role in roles else "default"](field, []):
    #             return url

    if not s.get_raw("hash"):
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


def confidential_url_serialize(serializer, url):
    # disabling download_url_serialize. TODO: Can be done for all the documents ?
    if serializer.get_raw("confidentiality") == "buyerOnly":
        return url_to_absolute(url)
    return download_url_serialize(serializer, url)


class DocumentSerializer(BaseSerializer):
    serializers = {
        "url": confidential_url_serialize,
    }

    def __init__(self, data: dict):
        self.private_fields = set()
        super().__init__(data)
        if data.get("confidentiality", "") == "buyerOnly":
            request = get_request()
            if (
                request.authenticated_role not in ("aboveThresholdReviewers", "sas")
                and not ("bid" in request.validated and is_item_owner(request, request.validated["bid"]))
                and (
                    (request.validated.get("tender") and not is_item_owner(request, request.validated["tender"]))
                    or (
                        request.validated.get("contract")
                        and not is_tender_owner(request, request.validated["contract"])
                    )
                )
            ):
                self.private_fields.add("url")
