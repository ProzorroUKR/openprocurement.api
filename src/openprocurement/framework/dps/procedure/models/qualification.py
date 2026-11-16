from openprocurement.api.constants import FrameworkType
from openprocurement.framework.core.procedure.models.qualification import (
    Qualification as BaseQualification,
)
from openprocurement.framework.dps.constants import DPSFrameworkType


class Qualification(BaseQualification):
    qualificationType: DPSFrameworkType = FrameworkType.DYNAMIC_PURCHASING_SYSTEM
