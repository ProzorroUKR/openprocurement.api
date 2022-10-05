from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.serializers.base import BaseSerializer, ListSerializer
from openprocurement.tender.core.procedure.serializers.feature import FeatureSerializer
from decimal import Decimal


def decimal_serializer(_, value):
    if isinstance(value, str):
        return Decimal(value)
    return value


class ValueSerializer(BaseSerializer):
    serializers = {
        "amount": decimal_serializer,
    }


class LotValueSerializer(BaseSerializer):
    serializers = {
        "value": ValueSerializer,
        "weightedValue": ValueSerializer,
    }


class AuctionBidSerializer(BaseSerializer):
    serializers = {
        "value": ValueSerializer,
        "weightedValue": ValueSerializer,
        "lotValues": ListSerializer(LotValueSerializer),
    }

    def __init__(self, data: dict):
        super().__init__(data)

        self.whitelist = {
            "id",
            "value",
            "weightedValue",
            "lotValues",
            "date",
            "participationUrl",
            "parameters",
            "status",
            "requirementResponses",
        }

        tender = get_tender()
        if tender["status"] not in ("draft", "active.enquiries", "active.tendering", "active.auction"):
            self.whitelist.add("tenderers")


class AuctionSerializer(BaseSerializer):

    serializers = {
        "bids": ListSerializer(AuctionBidSerializer),
        "features": ListSerializer(FeatureSerializer),
    }

    def __init__(self, data: dict):
        super().__init__(data)

        self.whitelist = {
            "tenderID",
            "dateModified",
            "bids",
            "items",
            "auctionPeriod",
            "minimalStep",
            "auctionUrl",
            "features",
            "lots",
            "criteria",
            # additionally we add more public fields
            # so auction-bridge won't have to make two requests
            # "awardCriteria",
            # "value",
            # "submissionMethodDetails",
            # "submissionMethodDetails",
            "id", "status",
            # "status" actually expected to be returned from auction post in the tests
            # the reason that test had worked is tender.status role had been used, not "auction_view". It was quite a bug
            "title", "title_en",
            "description", "description_en",
            "procurementMethodType",
            # "procuringEntity",
        }

        tender = get_tender()
        if tender["status"] not in ("draft", "active.enquiries", "active.tendering", "active.auction"):
            self.whitelist.add("awards")
