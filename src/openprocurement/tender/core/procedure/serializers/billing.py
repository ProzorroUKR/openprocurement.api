from openprocurement.api.procedure.serializers.base import (
    BaseSerializer,
    BaseUIDSerializer,
    ListSerializer,
)


class BillingBidSerializer(BaseSerializer):
    whitelist = {
        "id",
        "lotValues",
        "date",
        "status",
        "value",
        "owner",
    }


class BillingTenderSerializer(BaseUIDSerializer):
    serializers = {
        "bids": ListSerializer(BillingBidSerializer),
    }
    whitelist = {
        "id",
        "owner",
        "tenderID",
        "dateCreated",
        "date",
        "status",
        "value",
        "awardPeriod",
        "enquiryPeriod",
        "procurementMethodType",
        "lots",
        "bids",
        "awards",
        "contracts",
        "qualifications",
    }
