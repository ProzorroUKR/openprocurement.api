from schematics.types import StringType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import IsoDateTimeType
from openprocurement.tender.core.procedure.models.milestone import Milestone


class ContractMilestone(Milestone):
    status = StringType(choices=["notMet", "met"], default="notMet")
    dateMet = IsoDateTimeType()


class PatchContractMilestone(Model):
    status = StringType(choices=["met"], required=True)
