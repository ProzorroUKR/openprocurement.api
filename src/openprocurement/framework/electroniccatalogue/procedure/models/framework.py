from schematics.types import StringType
from openprocurement.api.models import ModelType

from openprocurement.framework.core.procedure.models.framework import (
    Framework as BaseFramework,
    PostFramework as BasePostFramework,
    PatchFramework as BasePatchFramework,
    PatchActiveFramework as BasePatchActiveFramework,
)
from openprocurement.framework.electroniccatalogue.constants import ELECTRONIC_CATALOGUE_TYPE
from openprocurement.framework.electroniccatalogue.procedure.models.organization import (
    CentralProcuringEntity,
    PatchActiveCentralProcuringEntity,
    PatchCentralProcuringEntity,
)


class PostFramework(BasePostFramework):
    frameworkType = StringType(default=ELECTRONIC_CATALOGUE_TYPE)
    procuringEntity = ModelType(CentralProcuringEntity, required=True)


class PatchFramework(BasePatchFramework):
    procuringEntity = ModelType(PatchCentralProcuringEntity)


class Framework(BaseFramework):
    frameworkType = StringType(default=ELECTRONIC_CATALOGUE_TYPE)
    procuringEntity = ModelType(CentralProcuringEntity, required=True)


class PatchActiveFramework(BasePatchActiveFramework):
    procuringEntity = ModelType(PatchActiveCentralProcuringEntity)
