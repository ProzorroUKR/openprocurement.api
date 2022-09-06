from openprocurement.api.models import Model
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.validation import validate_related_lot
from schematics.types import StringType, MD5Type


class LotValue(Model):
    relatedLot = MD5Type()
    subcontractingDetails = StringType()
    status = StringType(choices=["pending", "active", "unsuccessful"])

    date = StringType()


class PostLotValue(Model):
    relatedLot = MD5Type()
    subcontractingDetails = StringType()
    status = StringType(choices=["pending"], default="pending")

    def validate_relatedLot(self, data, related_lot):
        tender = get_tender()
        validate_related_lot(tender, related_lot)


class PatchLotValue(Model):
    relatedLot = MD5Type()
    subcontractingDetails = StringType()

    def validate_relatedLot(self, data, related_lot):
        if related_lot is not None:
            tender = get_tender()
            validate_related_lot(tender, related_lot)
