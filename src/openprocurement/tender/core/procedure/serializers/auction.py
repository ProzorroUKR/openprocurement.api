from decimal import Decimal

from openprocurement.api.procedure.serializers.base import (
    BaseSerializer,
    ListSerializer,
)
from openprocurement.tender.core.procedure.serializers.feature import FeatureSerializer


def decimal_serializer(value):
    if isinstance(value, str):
        return Decimal(value)
    return value


class AuctionValueSerializer(BaseSerializer):
    serializers = {
        "amount": decimal_serializer,
    }


class AuctionLotValueSerializer(BaseSerializer):
    serializers = {
        "value": AuctionValueSerializer,
        "weightedValue": AuctionValueSerializer,
    }


class AuctionBidSerializer(BaseSerializer):
    serializers = {
        "value": AuctionValueSerializer,
        "weightedValue": AuctionValueSerializer,
        "lotValues": ListSerializer(AuctionLotValueSerializer),
    }

    def __init__(self, data: dict, tender=None, **kwargs):
        super().__init__(data, tender=tender, **kwargs)

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

        if tender["status"] not in ("draft", "active.enquiries", "active.tendering", "active.auction"):
            self.whitelist.add("tenderers")


class AuctionSerializer(BaseSerializer):
    serializers = {
        "bids": ListSerializer(AuctionBidSerializer),
        "features": ListSerializer(FeatureSerializer),
    }

    def serialize(self, data, **kwargs) -> dict:
        kwargs["tender"] = self.raw
        return super().serialize(data, **kwargs)

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
            "id",
            "status",
            # "status" actually expected to be returned from auction post in the tests
            # the reason that test had worked is tender.status role had been used, not "auction_view". It was quite a bug
            "title",
            "title_en",
            "description",
            "description_en",
            "procurementMethodType",
            # "procuringEntity",
        }

        if data["status"] not in ("draft", "active.enquiries", "active.tendering", "active.auction"):
            self.whitelist.add("awards")
