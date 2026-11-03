from schematics.types import MD5Type, StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.value import Value


class CDPatchLotValue(Model):
    relatedLot = MD5Type()
    subcontractingDetails = StringType()
    status = StringType(choices=["pending", "active", "unsuccessful"], default="pending")
    date = StringType()


class CDLotValue(CDPatchLotValue):
    initialValue = ModelType(Value)  # field added by chronograph
    participationUrl = StringType()  # field added after auction


class CDPostLotValue(Model):
    relatedLot = MD5Type()
    subcontractingDetails = StringType()
    status = StringType(choices=["pending"], default="pending")
