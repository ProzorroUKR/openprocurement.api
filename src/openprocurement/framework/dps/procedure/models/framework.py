from schematics.types import StringType
from openprocurement.api.models import ModelType

from openprocurement.framework.core.procedure.models.framework import (
    Framework as BaseFramework,
    PostFramework as BasePostFramework,
    PatchFramework as BasePatchFramework,
    PatchActiveFramework as BasePatchActiveFramework,
)
from openprocurement.framework.dps.constants import DPS_TYPE
from openprocurement.framework.dps.procedure.models.organization import (
    PatchActiveProcuringEntity,
    ProcuringEntity,
    PatchProcuringEntity,
)


class PostFramework(BasePostFramework):
    frameworkType = StringType(default=DPS_TYPE)
    procuringEntity = ModelType(ProcuringEntity, required=True)


class PatchFramework(BasePatchFramework):
    procuringEntity = ModelType(PatchProcuringEntity)


class Framework(BaseFramework):
    frameworkType = StringType(default=DPS_TYPE)
    procuringEntity = ModelType(ProcuringEntity, required=True)


class PatchActiveFramework(BasePatchActiveFramework):
    procuringEntity = ModelType(PatchActiveProcuringEntity)
