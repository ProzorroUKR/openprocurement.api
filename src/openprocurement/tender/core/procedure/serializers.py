from openprocurement.tender.core.procedure.context import get_request
from openprocurement.api.utils import generate_docservice_url
from urllib.parse import urlparse, parse_qs
from string import hexdigits


def value_amount_to_float(_, value):
    if isinstance(value, dict) and "amount" in value:
        value["amount"] = float(value["amount"])
    return value


def lot_value_serializer(s, values):
    for item in values:
        item["value"] = value_amount_to_float(s, item["value"])
    return values


class BaseSerializer:
    _data: dict
    serializers: dict
    private_fields: set

    def __init__(self, data: dict):
        self._data = data

    def get_raw(self, k):
        return self._data.get(k)

    @property
    def data(self) -> dict:
        data = {
            k: self.serialize_value(k, v)
            for k, v in self._data.items()
            if k not in self.private_fields
        }
        return data

    def serialize_value(self, key, value):
        serializer = self.serializers.get(key)
        if serializer:
            value = serializer(self, value)
        return value


class BidSerializer(BaseSerializer):
    serializers = {
        "value": value_amount_to_float,
        "lotValues": lot_value_serializer,
    }
    private_fields = {
        "owner",
        "owner_token",
        "transfer_token",
    }


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
        path = [i for i in urlparse(url).path.split("/")
                if len(i) == 32 and not set(i).difference(hexdigits)]
        return generate_docservice_url(request, doc_id, False, "{}/{}".format(path[0], path[-1]))
    return generate_docservice_url(request, doc_id, False)

#  WARNING, there is a
#  `@subscriber(BeforeRender)`
#  `def beforerender(event):`
#  in openprocurement.api
#  that works globally for all the requests and to documents like {"url": "/tenders/uid/blabla"}
#  adds host: {"url": "http://localhost/tenders/uid/blabla"}
#  TODO: move it to the Serializer


class DocumentSerializer(BaseSerializer):
    serializers = {
        "url": download_url_serialize,
    }

    @property
    def data(self) -> dict:
        data = {
            k: self.serialize_value(k, v)
            for k, v in self._data.items()
        }
        return data

