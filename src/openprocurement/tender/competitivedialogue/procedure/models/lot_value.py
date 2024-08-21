from schematics.types import MD5Type, StringType

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.tender.core.procedure.validation import validate_related_lot


class LotValue(Model):
    relatedLot = MD5Type()
    subcontractingDetails = StringType()
    status = StringType(choices=["pending", "active", "unsuccessful"], default="pending")
    date = StringType()

    def validate_relatedLot(self, data, related_lot):
        tender = get_tender()
        validate_related_lot(tender, related_lot)


class PostLotValue(Model):
    relatedLot = MD5Type()
    subcontractingDetails = StringType()
    status = StringType(choices=["pending"], default="pending")

    def validate_relatedLot(self, data, related_lot):
        tender = get_tender()
        validate_related_lot(tender, related_lot)
