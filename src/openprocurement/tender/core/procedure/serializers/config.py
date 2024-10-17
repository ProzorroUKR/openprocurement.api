from openprocurement.api.constants import TENDER_CONFIG_OPTIONALITY
from openprocurement.api.context import get_request
from openprocurement.api.procedure.context import get_agreement
from openprocurement.api.procedure.serializers.config import BaseConfigSerializer
from openprocurement.api.utils import request_fetch_agreement
from openprocurement.tender.core.migrations.add_config_award_complain_duration import (
    award_complain_duration_populator,
)
from openprocurement.tender.core.migrations.add_config_cancellation_complain_duration import (
    cancellation_complain_duration_populator,
)
from openprocurement.tender.core.migrations.add_config_clarification_until_duration import (
    clarification_until_duration_populator,
)
from openprocurement.tender.core.migrations.add_config_complain_regulation_field import (
    tender_complain_regulation_populator,
)
from openprocurement.tender.core.migrations.add_config_complaints import (
    has_award_complaints_populator,
    has_cancellation_complaints_populator,
    has_tender_complaints_populator,
)
from openprocurement.tender.core.migrations.add_config_has_auction_field import (
    has_auction_populator,
)
from openprocurement.tender.core.migrations.add_config_has_prequalification_field import (
    has_prequalification_populator,
)
from openprocurement.tender.core.migrations.add_config_has_qualification_complains_field import (
    has_qualification_complaints_populator,
)
from openprocurement.tender.core.migrations.add_config_has_value_estimation import (
    has_value_estimation_populator,
)
from openprocurement.tender.core.migrations.add_config_has_value_restriction import (
    has_value_restriction_populator,
)
from openprocurement.tender.core.migrations.add_config_min_bids_number import (
    min_bids_number_populator,
)
from openprocurement.tender.core.migrations.add_config_pre_selection import (
    pre_selection_populator,
)
from openprocurement.tender.core.migrations.add_config_qualification_complain_duration import (
    qualification_complain_duration_populator,
)
from openprocurement.tender.core.migrations.add_qualification_duration import (
    qualification_duration_populator,
)


def has_auction_serializer(value):
    # TODO: remove serializer after migration
    if value is None and TENDER_CONFIG_OPTIONALITY["hasAuction"] is True:
        request = get_request()
        tender = request.validated.get("tender")
        data = request.validated.get("data")
        ignore_submission_method_details = tender is None
        return has_auction_populator(
            tender or data,
            ignore_submission_method_details=ignore_submission_method_details,
        )
    return value


def has_awarding_order_serializer(value):
    if value is None and TENDER_CONFIG_OPTIONALITY["hasAwardingOrder"] is True:
        return True
    return value


def has_value_restriction_serializer(value):
    if value is None and TENDER_CONFIG_OPTIONALITY["hasValueRestriction"] is True:
        request = get_request()
        tender = request.validated.get("tender") or request.validated.get("data")
        return has_value_restriction_populator(tender)
    return value


def currency_value_equality_serializer(value):
    # TODO: remove serializer after migration
    if value is None and TENDER_CONFIG_OPTIONALITY["valueCurrencyEquality"] is True:
        return True
    return value


def has_prequalification_serializer(value):
    # TODO: remove serializer after migration
    if value is None and TENDER_CONFIG_OPTIONALITY["hasPrequalification"] is True:
        request = get_request()
        tender = request.validated.get("tender")
        data = request.validated.get("data")
        return has_prequalification_populator(tender or data)
    return value


def min_bids_number_serializer(value):
    if value is None and TENDER_CONFIG_OPTIONALITY["minBidsNumber"] is True:
        request = get_request()
        tender = request.validated.get("tender") or request.validated.get("data")
        return min_bids_number_populator(tender)
    return value


def complain_regulation_serializer(value):
    if value is None and TENDER_CONFIG_OPTIONALITY["tenderComplainRegulation"] is True:
        request = get_request()
        tender = request.validated.get("tender") or request.validated.get("data")
        return tender_complain_regulation_populator(tender)
    return value


def pre_selection_serializer(value):
    if value is None and TENDER_CONFIG_OPTIONALITY["hasPreSelectionAgreement"] is True:
        request = get_request()
        tender = request.validated.get("tender") or request.validated.get("data")
        return pre_selection_populator(tender)
    return value


def has_tender_complaints_serializer(value):
    if value is None and TENDER_CONFIG_OPTIONALITY["hasTenderComplaints"] is True:
        request = get_request()
        tender = request.validated.get("tender") or request.validated.get("data")
        return has_tender_complaints_populator(tender)
    return value


def has_award_complaints_serializer(value):
    if value is None and TENDER_CONFIG_OPTIONALITY["hasAwardComplaints"] is True:
        request = get_request()
        tender = request.validated.get("tender") or request.validated.get("data")
        return has_award_complaints_populator(tender)
    return value


def has_cancellation_complaints_serializer(value):
    if value is None and TENDER_CONFIG_OPTIONALITY["hasCancellationComplaints"] is True:
        request = get_request()
        tender = request.validated.get("tender") or request.validated.get("data")
        return has_cancellation_complaints_populator(tender)
    return value


def has_value_estimation_serializer(value):
    if value is None and TENDER_CONFIG_OPTIONALITY["hasValueEstimation"] is True:
        request = get_request()
        tender = request.validated.get("tender") or request.validated.get("data")
        return has_value_estimation_populator(tender)
    return value


def has_qualification_complaints_serializer(value):
    if value is None and TENDER_CONFIG_OPTIONALITY["hasQualificationComplaints"] is True:
        request = get_request()
        tender = request.validated.get("tender") or request.validated.get("data")
        return has_qualification_complaints_populator(tender)
    return value


def award_complain_duration_serializer(value):
    if value is None and TENDER_CONFIG_OPTIONALITY["awardComplainDuration"] is True:
        request = get_request()
        tender = request.validated.get("tender") or request.validated.get("data")
        return award_complain_duration_populator(tender)
    return value


def qualification_complain_duration_serializer(value):
    if value is None and TENDER_CONFIG_OPTIONALITY["qualificationComplainDuration"] is True:
        request = get_request()
        tender = request.validated.get("tender") or request.validated.get("data")
        return qualification_complain_duration_populator(tender)
    return value


def clarification_until_duration_serializer(value):
    if value is None and TENDER_CONFIG_OPTIONALITY["clarificationUntilDuration"] is True:
        request = get_request()
        tender = request.validated.get("tender") or request.validated.get("data")
        return clarification_until_duration_populator(tender)
    return value


def qualification_duration_serializer(value):
    if value is None and TENDER_CONFIG_OPTIONALITY["qualificationDuration"] is True:
        request = get_request()
        tender = request.validated.get("tender") or request.validated.get("data")
        return qualification_duration_populator(tender)
    return value


def restricted_serializer(value):
    if value is None and TENDER_CONFIG_OPTIONALITY["restricted"] is True:
        request = get_request()
        tender = request.validated.get("tender") or request.validated.get("data")
        agreements = tender.get("agreements")
        if agreements:
            request_fetch_agreement(get_request(), agreements[0]["id"], raise_error=False)
            agreement = get_agreement()
            if agreement and agreement["config"]["restricted"] is True:
                return True
        return False
    return value


def cancellation_complain_duration_serializer(value):
    if value is None and TENDER_CONFIG_OPTIONALITY["cancellationComplainDuration"] is True:
        request = get_request()
        tender = request.validated.get("tender") or request.validated.get("data")
        return cancellation_complain_duration_populator(tender)
    return value


class TenderConfigSerializer(BaseConfigSerializer):
    serializers = {
        "hasAuction": has_auction_serializer,
        "hasAwardingOrder": has_awarding_order_serializer,
        "hasValueRestriction": has_value_restriction_serializer,
        "valueCurrencyEquality": currency_value_equality_serializer,
        "hasPrequalification": has_prequalification_serializer,
        "minBidsNumber": min_bids_number_serializer,
        "hasPreSelectionAgreement": pre_selection_serializer,
        "hasTenderComplaints": has_tender_complaints_serializer,
        "hasAwardComplaints": has_award_complaints_serializer,
        "hasCancellationComplaints": has_cancellation_complaints_serializer,
        "hasValueEstimation": has_value_estimation_serializer,
        "hasQualificationComplaints": has_qualification_complaints_serializer,
        "tenderComplainRegulation": complain_regulation_serializer,
        "qualificationComplainDuration": qualification_complain_duration_serializer,
        "awardComplainDuration": award_complain_duration_serializer,
        "cancellationComplainDuration": cancellation_complain_duration_serializer,
        "clarificationUntilDuration": clarification_until_duration_serializer,
        "qualificationDuration": qualification_duration_serializer,
        "restricted": restricted_serializer,
    }
