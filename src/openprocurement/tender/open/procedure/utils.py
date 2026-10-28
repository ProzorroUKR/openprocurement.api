from openprocurement.tender.open.constants import (
    PROCUREMENT_ASPECT_EU,
    PROCUREMENT_ASPECT_UA,
)


def get_open_tendering_variant(tender) -> str | None:
    """openTendering: the UA/EU variant of the tender set by its procurementAspects field (None if not set)"""
    aspects = tender.get("procurementAspects") if isinstance(tender, dict) else None
    if not isinstance(aspects, list):
        return None
    if PROCUREMENT_ASPECT_EU in aspects:
        return PROCUREMENT_ASPECT_EU
    if PROCUREMENT_ASPECT_UA in aspects:
        return PROCUREMENT_ASPECT_UA
    return None
