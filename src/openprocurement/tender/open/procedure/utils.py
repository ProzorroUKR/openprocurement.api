from openprocurement.tender.open.constants import OPEN_TENDERING_EU, OPEN_TENDERING_UA


def get_open_tendering_variant(tender) -> str | None:
    """openTendering: the UA/EU variant of the tender set by its procedure.euPublished field (None if not set)"""
    procedure = tender.get("procedure") if isinstance(tender, dict) else None
    eu_published = procedure.get("euPublished") if isinstance(procedure, dict) else None
    if eu_published is True:
        return OPEN_TENDERING_EU
    if eu_published is False:
        return OPEN_TENDERING_UA
    return None
