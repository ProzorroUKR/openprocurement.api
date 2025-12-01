from copy import deepcopy
from typing import Any

from openprocurement.api.constants import CAUSE_DETAILS_MAPPING_ALL
from openprocurement.tender.core.procedure.serializers.tender import (
    TenderBaseSerializer,
)


def set_cause_details_from_dictionary(obj):
    prev_obj = deepcopy(obj)
    procurement_method_type = obj["procurementMethodType"]
    if cause_code := obj["causeDetails"].get("code"):
        if cause_code not in CAUSE_DETAILS_MAPPING_ALL[procurement_method_type]:
            return prev_obj
        obj["causeDetails"].update(
            {
                "scheme": CAUSE_DETAILS_MAPPING_ALL[procurement_method_type][cause_code]["scheme"],
                "title": CAUSE_DETAILS_MAPPING_ALL[procurement_method_type][cause_code]["title_uk"],
                "title_en": CAUSE_DETAILS_MAPPING_ALL[procurement_method_type][cause_code]["title_en"],
            }
        )
    return obj


def convert_cause_to_cause_details(obj):
    obj["causeDetails"] = {}
    for field_name, field_alt_name in [
        ("cause", "code"),
        ("causeDescription", "description"),
        ("causeDescription_en", "description_en"),
    ]:
        if obj.get(field_name):
            obj["causeDetails"][field_alt_name] = obj[field_name]
    obj = set_cause_details_from_dictionary(obj)
    return obj


class LimitedTenderBaseSerializer(TenderBaseSerializer):
    def serialize(self, data: dict[str, Any], tender=None, **kwargs) -> dict[str, Any]:
        data = data.copy()
        if not data.get("causeDetails") and data.get("cause"):
            convert_cause_to_cause_details(data)
        return super().serialize(data, **kwargs)
