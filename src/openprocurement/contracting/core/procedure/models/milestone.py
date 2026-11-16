from typing import Literal

from openprocurement.api.procedure.models.milestone import BaseMilestone
from openprocurement.api.procedure.types import IsoDateTime


class ContractMilestone(BaseMilestone):
    # todo: add later logic for updating milestone's status with met/unMet
    status: Literal["scheduled"] = "scheduled"
    dateMet: IsoDateTime | None = None
