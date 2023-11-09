from openprocurement.api.context import get_request
from openprocurement.api.constants import TENDER_CONFIG_OPTIONALITY
from openprocurement.tender.core.migrations.add_config_has_auction_field import has_auction_populator
from openprocurement.tender.core.migrations.add_config_min_bids_number import min_bids_number_populator
from openprocurement.tender.core.migrations.add_config_has_value_restriction import has_value_restriction_populator
from openprocurement.tender.core.migrations.add_config_has_prequalification_field import has_prequalification_populator
from openprocurement.tender.core.migrations.add_config_pre_selection import pre_selection_populator
from openprocurement.tender.core.procedure.serializers.base import BaseSerializer


def has_auction_serializer(obj, value):
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


def has_awarding_order_serializer(obj, value):
    if value is None and TENDER_CONFIG_OPTIONALITY["hasAwardingOrder"] is True:
        return True
    return value


def has_value_restriction_serializer(obj, value):
    if value is None and TENDER_CONFIG_OPTIONALITY["hasValueRestriction"] is True:
        request = get_request()
        tender = request.validated.get("tender") or request.validated.get("data")
        return has_value_restriction_populator(tender)
    return value


def currency_value_equality_serializer(obj, value):
    # TODO: remove serializer after migration
    if value is None and TENDER_CONFIG_OPTIONALITY["valueCurrencyEquality"] is True:
        return True
    return value


def has_prequalification_serializer(obj, value):
    # TODO: remove serializer after migration
    if value is None and TENDER_CONFIG_OPTIONALITY["hasPrequalification"] is True:
        request = get_request()
        tender = request.validated.get("tender")
        data = request.validated.get("data")
        return has_prequalification_populator(tender or data)
    return value


def min_bids_number_serializer(obj, value):
    if value is None and TENDER_CONFIG_OPTIONALITY["minBidsNumber"] is True:
        request = get_request()
        tender = request.validated.get("tender") or request.validated.get("data")
        return min_bids_number_populator(tender)
    return value


def pre_selection_serializer(obj, value):
    if value is None and TENDER_CONFIG_OPTIONALITY["hasPreSelectionAgreement"] is True:
        request = get_request()
        tender = request.validated.get("tender") or request.validated.get("data")
        return pre_selection_populator(tender)
    return value


class TenderConfigSerializer(BaseSerializer):
    def __init__(self, data: dict):
        super().__init__(data)
        for field_name in self.serializers.keys():
            if field_name not in self._data:
                self._data[field_name] = None

    serializers = {
        "hasAuction": has_auction_serializer,
        "hasAwardingOrder": has_awarding_order_serializer,
        "hasValueRestriction": has_value_restriction_serializer,
        "valueCurrencyEquality": currency_value_equality_serializer,
        "hasPrequalification": has_prequalification_serializer,
        "minBidsNumber": min_bids_number_serializer,
        "hasPreSelectionAgreement": pre_selection_serializer,
    }
