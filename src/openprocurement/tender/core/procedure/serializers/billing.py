from openprocurement.api.procedure.serializers.base import (
    BaseSerializer,
    BaseUIDSerializer,
    ListSerializer,
)


class BillingBidSerializer(BaseSerializer):
    public_fields = {
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
    public_fields = {
        "id",
        "owner",
        "tenderID",
        "dateCreated",
        "date",
        "status",
        "value",
        "awardPeriod",
        "enquiryPeriod",
        "tenderPeriod",
        "procurementMethodType",
        "lots",
        "bids",
        "awards",
        "contracts",
        "qualifications",
    }
