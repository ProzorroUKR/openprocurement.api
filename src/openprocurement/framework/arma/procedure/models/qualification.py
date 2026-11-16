from openprocurement.api.constants import FrameworkType
from openprocurement.framework.arma.constants import ARMAFrameworkType
from openprocurement.framework.core.procedure.models.qualification import (
    Qualification as BaseQualification,
)


class Qualification(BaseQualification):
    qualificationType: ARMAFrameworkType = FrameworkType.ASSET_RECOVERY_MANAGEMENT_AGENCY
