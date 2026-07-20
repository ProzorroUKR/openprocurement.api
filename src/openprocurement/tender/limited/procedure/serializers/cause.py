from typing import Any

from openprocurement.api.deprecated.cause_details import PROCUREMENT_METHOD_TYPE_TO_FROZEN_CAUSE_DETAILS_MAPPING_ALL
from openprocurement.api.procedure.serializers.base import BaseSerializer


def get_cause_details_reference(tender: dict[str, Any], cause_details_mapping: dict[str, Any]) -> dict[str, Any]:
    procurement_method_type = tender["procurementMethodType"]
    return cause_details_mapping.get(procurement_method_type, {})


def enrich_cause_details(
    cause_details: dict[str, Any] | None,
    cause_details_reference: dict[str, Any],
    force: bool = False,
) -> dict[str, Any] | None:
    if not cause_details or not cause_details_reference:
        return cause_details

    cause_details = cause_details.copy()
    cause_code = cause_details.get("code")
    if not cause_code:
        return cause_details

    cause_details_entry = cause_details_reference.get(cause_code)
    if not cause_details_entry:
        return cause_details

    for field_name, reference_field_name in [
        ("scheme", "scheme"),
        ("title", "title_uk"),
        ("title_en", "title_en"),
        ("uri", "uri"),
    ]:
        if not force and cause_details.get(field_name):
            continue
        if reference_field_name not in cause_details_entry:
            continue
        cause_details[field_name] = cause_details_entry[reference_field_name]
    return cause_details


class CauseDetailsSerializer(BaseSerializer):
    # TODO: remove after migration

    def serialize(self, data: dict[str, Any] | None, **kwargs) -> dict[str, Any]:
        mapping = PROCUREMENT_METHOD_TYPE_TO_FROZEN_CAUSE_DETAILS_MAPPING_ALL
        cause_details_reference = get_cause_details_reference(kwargs["tender"], mapping)
        data = enrich_cause_details(data, cause_details_reference)
        return super().serialize(data, **kwargs)
