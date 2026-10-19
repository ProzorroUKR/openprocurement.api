from schematics.types import StringType

from openprocurement.framework.arma.constants import ARMA_TYPE
from openprocurement.framework.core.procedure.models.qualification import (
    Qualification as BaseQualification,
)


class Qualification(BaseQualification):
    qualificationType = StringType(default=ARMA_TYPE, required=True)
