from enum import StrEnum
from typing import Literal

from openprocurement.api.procedure.models.base import Model


class LimitedCauseScheme(StrEnum):
    DECREE_1178 = "DECREE1178"
    LAW_922 = "LAW922"
    DECREE_1275 = "DECREE1275"


class LimitedCauseDetails(Model):
    code: str
    title: str | None = None
    title_en: str | None = None
    scheme: (
        Literal[LimitedCauseScheme.DECREE_1178, LimitedCauseScheme.LAW_922, LimitedCauseScheme.DECREE_1275] | None
    ) = None
    description: str | None = None
    description_en: str | None = None
    uri: str | None = None
