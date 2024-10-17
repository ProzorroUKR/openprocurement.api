from decimal import Decimal

from openprocurement.api.procedure.serializers.base import (
    BaseSerializer,
    ListSerializer,
)
from openprocurement.tender.core.procedure.serializers.auction import (
    AuctionSerializer as BaseAuctionSerializer,
)
from openprocurement.tender.core.procedure.serializers.feature import FeatureSerializer
from openprocurement.tender.core.procedure.serializers.parameter import (
    ParameterSerializer,
)
from openprocurement.tender.esco.procedure.serializers.bid import BidSerializer
from openprocurement.tender.esco.procedure.serializers.value import ValueSerializer


def decimal_serializer(value):
    if isinstance(value, str):
        return Decimal(value)
    return value


class AuctionLotValueSerializer(BaseSerializer):
    serializers = {
        "value": ValueSerializer,
        "weightedValue": ValueSerializer,
    }


class AuctionBidSerializer(BidSerializer):
    serializers = {
        "parameters": ListSerializer(ParameterSerializer),
        "value": ValueSerializer,
        "weightedValue": ValueSerializer,
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
            "status",
            "participationUrl",
            "parameters",
        }

        if tender["status"] not in ("draft", "active.enquiries", "active.tendering", "active.auction"):
            self.whitelist.add("tenderers")


class AuctionAwardSerializer(BaseSerializer):
    serializers = {
        "value": ValueSerializer,
    }


class AuctionLotSerializer(BaseSerializer):
    serializers = {
        "yearlyPaymentsPercentageRange": decimal_serializer,
        "minimalStepPercentage": decimal_serializer,
    }


class AuctionSerializer(BaseAuctionSerializer):
    serializers = {
        "bids": ListSerializer(AuctionBidSerializer),
        "awards": ListSerializer(AuctionAwardSerializer),
        "NBUdiscountRate": decimal_serializer,
        "yearlyPaymentsPercentageRange": decimal_serializer,
        "minimalStepPercentage": decimal_serializer,
        "lots": ListSerializer(AuctionLotSerializer),
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
            "minimalStepPercentage",
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
            "NBUdiscountRate",
            "noticePublicationDate",
            "fundingKind",
            "yearlyPaymentsPercentageRange",
        }

        if data["status"] not in ("draft", "active.enquiries", "active.tendering", "active.auction"):
            self.whitelist.add("awards")
