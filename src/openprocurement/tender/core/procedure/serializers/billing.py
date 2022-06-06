from openprocurement.tender.core.procedure.serializers.base import (
    BaseUIDSerializer,
    BaseSerializer,
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
        "_id",
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
