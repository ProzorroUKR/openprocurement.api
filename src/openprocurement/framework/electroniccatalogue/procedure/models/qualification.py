from schematics.types import StringType
from openprocurement.framework.core.procedure.models.qualification import Qualification as BaseQualification
from openprocurement.framework.electroniccatalogue.constants import ELECTRONIC_CATALOGUE_TYPE


class Qualification(BaseQualification):
    qualificationType = StringType(default=ELECTRONIC_CATALOGUE_TYPE, required=True)
