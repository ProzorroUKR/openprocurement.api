from openprocurement.tender.core.procedure.serializers import (
    BidSerializer as BaseBidSerializer,
    DocumentSerializer as BaseDocumentSerializer,
    download_url_serialize,
)
from openprocurement.tender.core.procedure.utils import is_item_owner
from openprocurement.tender.core.procedure.context import get_request


class BidSerializer(BaseBidSerializer):
    whitelist = None

    def __init__(self, data: dict):
        super().__init__(data)
        if data.get("status") in ("invalid", "deleted"):
            self.whitelist = {"id", "status"}

    @property
    def data(self) -> dict:
        if self.whitelist:
            data = {
                k: self.serialize_value(k, v)
                for k, v in self._data.items()
                if k in self.whitelist
            }
            return data
        return super().data


def confidential_url_serialize(serializer, url):
    # disabling download_url_serialize. TODO: Can be done for all the documents ?
    if serializer.get_raw("confidentiality") == "buyerOnly":
        return url
    return download_url_serialize(serializer, url)


class ConfidentialDocumentSerializer(BaseDocumentSerializer):
    serializers = {
        "url": confidential_url_serialize,
    }

    @property
    def data(self) -> dict:
        skip = set()
        if self._data.get("confidentiality", "") == "buyerOnly":
            request = get_request()
            if (
                request.authenticated_role not in ("aboveThresholdReviewers", "sas")
                and not is_item_owner(request, request.validated["bid"])
                and not is_item_owner(request, request.validated["tender"])
            ):
                skip.add("url")

        data = {
            k: self.serialize_value(k, v)
            for k, v in self._data.items()
            if k not in skip
        }
        return data
