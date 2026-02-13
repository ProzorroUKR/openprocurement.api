from schematics.types import StringType

from openprocurement.api.procedure.types import IsoDateTimeType
from openprocurement.tender.core.procedure.models.milestone import Milestone


class ContractMilestone(Milestone):
    # todo: add later logic for updating milestone's status with met/unMet
    status = StringType(choices=["scheduled"], default="scheduled")
    dateMet = IsoDateTimeType()
    relatedLot = None


ContractMilestone._fields.pop("relatedLot", None)
