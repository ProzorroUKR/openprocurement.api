from openprocurement.api.constants import FrameworkType
from openprocurement.framework.core.procedure.models.qualification import (
    Qualification as BaseQualification,
)
from openprocurement.framework.ifi.constants import IFIFrameworkType


class Qualification(BaseQualification):
    qualificationType: IFIFrameworkType = FrameworkType.INTERNATIONAL_FINANCIAL_INSTITUTIONS
