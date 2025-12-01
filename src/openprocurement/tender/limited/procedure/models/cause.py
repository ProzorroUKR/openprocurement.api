from enum import StrEnum

from schematics.types import StringType

from openprocurement.api.procedure.models.base import Model


class CauseScheme(StrEnum):
    DECREE_1178 = "DECREE1178"
    LAW_922 = "LAW922"


class CauseDetails(Model):
    code = StringType(required=True)
    title = StringType()
    title_en = StringType()
    scheme = StringType(
        choices=[
            CauseScheme.DECREE_1178.value,
            CauseScheme.LAW_922.value,
        ],
    )
    description = StringType()
    description_en = StringType()
