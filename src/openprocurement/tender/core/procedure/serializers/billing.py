from openprocurement.api.procedure.serializers.base import (
    BaseSerializer,
    BaseUIDSerializer,
    ListSerializer,
)
from openprocurement.tender.core.procedure.serializers.complaint import ComplaintSerializer


class BillingBidSerializer(BaseSerializer):
    public_fields = {
        "id",
        "lotValues",
        "date",
        "submissionDate",
        "status",
        "value",
        "initialValue",
        "owner",
    }


class BillingTenderSerializer(BaseUIDSerializer):
    serializers = {
        "bids": ListSerializer(BillingBidSerializer),
        "complaints": ListSerializer(ComplaintSerializer),
    }
    public_fields = {
        "id",
        "owner",
        "agreement",
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
        "complaints",
    }
