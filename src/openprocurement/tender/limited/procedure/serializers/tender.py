from copy import deepcopy
from typing import Any

from openprocurement.tender.core.procedure.serializers.tender import (
    TenderBaseSerializer,
)
from openprocurement.tender.limited.constants import REPORTING
from openprocurement.tender.limited.procedure.models.cause import CAUSE_SCHEME_MAPPING


def convert_cause_to_cause_details(obj):
    prev_obj = deepcopy(obj)
    obj["causeDetails"] = {}
    for field_name, field_alt_name in [
        ("cause", "title"),
        ("causeDescription", "description"),
        ("causeDescription_en", "description_en"),
    ]:
        if obj.get(field_name):
            obj["causeDetails"][field_alt_name] = obj[field_name]
    if obj["procurementMethodType"] == REPORTING:
        if obj["cause"] == "hematopoieticStemCells":
            obj["causeDetails"]["scheme"] = "LAW922"
        else:
            obj["causeDetails"]["scheme"] = "DECREE1178"
    else:
        obj["causeDetails"]["scheme"] = "LAW922"
    if obj["causeDetails"]["title"] not in CAUSE_SCHEME_MAPPING[obj["causeDetails"]["scheme"]]:
        return prev_obj
    return obj


class LimitedTenderBaseSerializer(TenderBaseSerializer):
    def serialize(self, data: dict[str, Any], tender=None, **kwargs) -> dict[str, Any]:
        data = data.copy()
        if not data.get("causeDetails") and data.get("cause"):
            convert_cause_to_cause_details(data)
        return super().serialize(data, **kwargs)
