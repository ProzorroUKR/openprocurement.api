from schematics.types import StringType

from openprocurement.tender.core.procedure.models.criterion import (
    Criterion as BaseCriterion,
)
from openprocurement.tender.core.procedure.models.criterion import (
    PatchCriterion as BasePatchCriterion,
)


class PatchLimitedCriterion(BasePatchCriterion):
    source = StringType(choices=["procuringEntity"])


class LimitedCriterion(BaseCriterion):
    source = StringType(
        choices=["procuringEntity"],
        required=True,
    )
