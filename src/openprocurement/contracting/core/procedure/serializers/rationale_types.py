from datetime import datetime
from typing import Any

from openprocurement.api.constants import (
    CAUSE_TO_RATIONALE_TYPES_MAPPING_ALL,
    TENDERS_CONTRACT_CHANGE_BASED_ON_DECREE_1178,
    TZ,
)
from openprocurement.api.procedure.serializers.base import BaseSerializer

DATE_BEFORE_TYPES_SPLITTING = TZ.localize(datetime(year=2022, month=10, day=12))


def get_change_rationale_types_reference(tender, cause_to_types_mapping: dict[str, dict[str, Any]]):
    if not tender or not cause_to_types_mapping:
        return {}

    # Old tenders use LAW922
    date_created = tender.get("dateCreated")
    date_created = datetime.fromisoformat(date_created) if date_created else None
    if date_created and date_created < DATE_BEFORE_TYPES_SPLITTING:
        return cause_to_types_mapping["LAW922"]

    # New causeDetails.scheme logic
    cause_details = tender.get("causeDetails", {})
    cause_scheme = cause_details.get("scheme")
    if cause_scheme in cause_to_types_mapping.keys():
        return cause_to_types_mapping[cause_scheme]

    # Some procurementMethodType use DECREE1178
    if tender["procurementMethodType"] in TENDERS_CONTRACT_CHANGE_BASED_ON_DECREE_1178:
        return cause_to_types_mapping["DECREE1178"]

    # Default to LAW922
    return cause_to_types_mapping["LAW922"]


def enrich_contract_change_rationale_types(
    rationale_types: dict[str, Any] | None,
    rationale_types_reference: dict[str, Any] | None,
    force: bool = False,
) -> dict[str, Any] | None:
    # TODO: remove after migration

    if not rationale_types or not rationale_types_reference:
        return rationale_types

    enriched = {}
    for code, entry in rationale_types.items():
        entry = entry.copy()
        reference_entry = rationale_types_reference.get(code)
        if reference_entry:
            for field_name in ("uri", "scheme"):
                if not force and entry.get(field_name):
                    continue
                if field_name in reference_entry:
                    entry[field_name] = reference_entry[field_name]
        enriched[code] = entry
    return enriched


class ContractChangeRationaleTypesSerializer(BaseSerializer):
    # TODO: remove after migration

    def serialize(self, data: dict[str, Any] | None, **kwargs) -> dict[str, Any]:
        mapping = CAUSE_TO_RATIONALE_TYPES_MAPPING_ALL
        rationale_types_reference = get_change_rationale_types_reference(kwargs.get("tender"), mapping)
        data = enrich_contract_change_rationale_types(data, rationale_types_reference)
        return super().serialize(data, **kwargs)
