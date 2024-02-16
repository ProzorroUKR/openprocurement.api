from openprocurement.tender.core.procedure.utils import find_lot
from openprocurement.tender.core.procedure.validation import (
    validate_lot_value_currency,
    validate_lot_value_vat,
)


def validate_lotvalue_value(tender, related_lot, value):
    if not related_lot:
        return
    if tender.get("status") in ("invalid", "deleted", "draft"):
        return
    lot = find_lot(tender, related_lot)
    if lot and value:
        tender_lot_value = lot.get("minValue")
        validate_lot_value_currency(tender_lot_value, value, name="minValue")
        validate_lot_value_vat(tender_lot_value, value, name="minValue")
