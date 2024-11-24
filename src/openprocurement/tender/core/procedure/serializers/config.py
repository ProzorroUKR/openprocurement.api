from openprocurement.api.constants import (
    TENDER_CONFIG_JSONSCHEMAS,
    TENDER_CONFIG_OPTIONALITY,
)
from openprocurement.api.context import get_request
from openprocurement.api.procedure.serializers.config import BaseConfigSerializer


def tender_config_default_value(key):
    request = get_request()
    tender = request.validated.get("tender") or request.validated.get("data")
    procurement_method_type = tender.get("procurementMethodType")
    config_schema = TENDER_CONFIG_JSONSCHEMAS.get(procurement_method_type)
    return config_schema["properties"][key]["default"]


def tender_config_default_serializer(key):
    def serializer(value):
        if value is None and TENDER_CONFIG_OPTIONALITY[key] is True:
            return tender_config_default_value(key)
        return value

    return serializer


class TenderConfigSerializer(BaseConfigSerializer):
    serializers = {
        "hasAuction": tender_config_default_serializer("hasAuction"),
        "hasAwardingOrder": tender_config_default_serializer("hasAwardingOrder"),
        "hasValueRestriction": tender_config_default_serializer("hasValueRestriction"),
        "valueCurrencyEquality": tender_config_default_serializer("valueCurrencyEquality"),
        "hasPrequalification": tender_config_default_serializer("hasPrequalification"),
        "minBidsNumber": tender_config_default_serializer("minBidsNumber"),
        "hasPreSelectionAgreement": tender_config_default_serializer("hasPreSelectionAgreement"),
        "hasTenderComplaints": tender_config_default_serializer("hasTenderComplaints"),
        "hasAwardComplaints": tender_config_default_serializer("hasAwardComplaints"),
        "hasCancellationComplaints": tender_config_default_serializer("hasCancellationComplaints"),
        "hasValueEstimation": tender_config_default_serializer("hasValueEstimation"),
        "hasQualificationComplaints": tender_config_default_serializer("hasQualificationComplaints"),
        "tenderComplainRegulation": tender_config_default_serializer("tenderComplainRegulation"),
        "qualificationComplainDuration": tender_config_default_serializer("qualificationComplainDuration"),
        "awardComplainDuration": tender_config_default_serializer("awardComplainDuration"),
        "cancellationComplainDuration": tender_config_default_serializer("cancellationComplainDuration"),
        "clarificationUntilDuration": tender_config_default_serializer("clarificationUntilDuration"),
        "qualificationDuration": tender_config_default_serializer("qualificationDuration"),
        "restricted": tender_config_default_serializer("restricted"),
    }
