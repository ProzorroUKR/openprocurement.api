from openprocurement.api.constants import FrameworkType
from openprocurement.framework.core.procedure.models.qualification import (
    Qualification as BaseQualification,
)
from openprocurement.framework.electroniccatalogue.constants import ElectronicCatalogueFrameworkType


class Qualification(BaseQualification):
    qualificationType: ElectronicCatalogueFrameworkType = FrameworkType.ELECTRONIC_CATALOGUE
