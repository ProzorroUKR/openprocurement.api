from decimal import Decimal

from openprocurement.api.procedure.serializers.base import (
    BaseSerializer,
    BaseUIDSerializer,
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

        self.public_fields: set[str] = {
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
            self.public_fields.add("tenderers")


class AuctionSerializer(BaseUIDSerializer):
    serializers = {
        "bids": ListSerializer(AuctionBidSerializer),
        "features": ListSerializer(FeatureSerializer),
    }

    def serialize(self, data, **kwargs) -> dict:
        kwargs["tender"] = self.raw
        return super().serialize(data, **kwargs)

    def __init__(self, data: dict):
        super().__init__(data)

        self.public_fields: set[str] = {
            "id",
            "status",
            "title",
            "title_en",
            "description",
            "description_en",
            "procurementMethodType",
            "mode",
            "awardCriteria",
            "procuringEntity",
            "tenderID",
            "dateModified",
            "bids",
            "awards",
            "lots",
            "items",
            "features",
            "criteria",
            "value",
            "minimalStep",
            "minimalStepPercentage",
            "submissionMethodDetails",
            "NBUdiscountRate",
            "noticePublicationDate",
            "fundingKind",
            "yearlyPaymentsPercentageRange",
            "auctionPeriod",
            "auctionUrl",
        }
