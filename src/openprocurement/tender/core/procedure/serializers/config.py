from openprocurement.api.constants import (
    TENDER_CO_CONFIG_JSONSCHEMAS,
    TENDER_CONFIG_JSONSCHEMAS,
)
from openprocurement.api.constants_env import TENDER_CONFIG_OPTIONALITY
from openprocurement.api.context import get_request
from openprocurement.api.procedure.context import get_agreement
from openprocurement.api.procedure.serializers.config import BaseConfigSerializer
from openprocurement.api.utils import request_fetch_agreement


def tender_config_default_value(tender, key):
    procurement_method_type = tender.get("procurementMethodType")
    if procurement_method_type == "competitiveOrdering":
        return tender_config_co_default_value(tender, key)
    config_schema = TENDER_CONFIG_JSONSCHEMAS.get(procurement_method_type)
    return config_schema["properties"][key]["default"]


def tender_config_co_default_value(tender, key):
    agreements = tender.get("agreements")
    request_fetch_agreement(get_request(), agreements[0]["id"])
    agreement = get_agreement()
    if agreement.get("items"):
        config_schema_name = "competitiveOrdering.short"
    else:
        config_schema_name = "competitiveOrdering.long"
    config_schema = TENDER_CO_CONFIG_JSONSCHEMAS.get(config_schema_name)
    return config_schema["properties"][key]["default"]


def tender_config_default_serializer(key, migration_func=None):
    def serializer(value):
        if value is not None:
            return value

        request = get_request()
        tender_src = request.validated.get("tender_src")
        tender = request.validated.get("tender")

        # if value is None and this is existing tender
        # that means it was not migrated yet
        # use migration function to fill value until migration is done
        is_existing_tender = bool(tender_src)

        # if key is optional, we can use default value
        is_optional = TENDER_CONFIG_OPTIONALITY[key] is True

        if not is_existing_tender and not is_optional:
            return value

        if is_existing_tender and migration_func:
            return migration_func(tender)

        return tender_config_default_value(tender, key)

    return serializer


def tender_config_min_tendering_duration_migrate_value(tender):
    procurement_method_type = tender.get("procurementMethodType")
    if procurement_method_type == "competitiveOrdering":
        return 3
    return tender_config_default_value(tender, "minTenderingDuration")


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
        "minTenderingDuration": tender_config_default_serializer(
            "minTenderingDuration",
            migration_func=tender_config_min_tendering_duration_migrate_value,
        ),
        "restricted": tender_config_default_serializer("restricted"),
    }
