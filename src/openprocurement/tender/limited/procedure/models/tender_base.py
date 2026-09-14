from enum import StrEnum

from schematics.types import StringType

from openprocurement.api.procedure.models.base import Model


class LimitedCauseScheme(StrEnum):
    DECREE_1178 = "DECREE1178"
    LAW_922 = "LAW922"
    DECREE_1275 = "DECREE1275"


class LimitedCauseDetails(Model):
    code = StringType(required=True)
    title = StringType()
    title_en = StringType()
    scheme = StringType(
        choices=[
            LimitedCauseScheme.DECREE_1178.value,
            LimitedCauseScheme.LAW_922.value,
            LimitedCauseScheme.DECREE_1275.value,
        ],
    )
    description = StringType()
    description_en = StringType()
    uri = StringType()
