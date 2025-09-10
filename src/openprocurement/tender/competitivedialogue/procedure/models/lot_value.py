from schematics.types import MD5Type, StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.value import Value
from openprocurement.tender.core.procedure.validation import validate_related_lot


class PatchLotValue(Model):
    relatedLot = MD5Type()
    subcontractingDetails = StringType()
    status = StringType(choices=["pending", "active", "unsuccessful"], default="pending")
    date = StringType()

    def validate_relatedLot(self, data, related_lot):
        tender = get_tender()
        validate_related_lot(tender, related_lot)


class LotValue(PatchLotValue):
    initialValue = ModelType(Value)  # field added by chronograph
    participationUrl = StringType()  # field added after auction


class PostLotValue(Model):
    relatedLot = MD5Type()
    subcontractingDetails = StringType()
    status = StringType(choices=["pending"], default="pending")

    def validate_relatedLot(self, data, related_lot):
        tender = get_tender()
        validate_related_lot(tender, related_lot)
