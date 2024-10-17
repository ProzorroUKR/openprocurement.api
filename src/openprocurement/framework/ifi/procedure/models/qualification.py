from schematics.types import StringType

from openprocurement.framework.core.procedure.models.qualification import (
    Qualification as BaseQualification,
)
from openprocurement.framework.ifi.constants import IFI_TYPE


class Qualification(BaseQualification):
    qualificationType = StringType(default=IFI_TYPE, required=True)
