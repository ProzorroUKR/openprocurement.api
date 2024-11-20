from schematics.types import StringType

from openprocurement.api.procedure.types import ModelType
from openprocurement.framework.core.procedure.models.framework import (
    Framework as BaseFramework,
)
from openprocurement.framework.core.procedure.models.framework import (
    PatchActiveFramework as BasePatchActiveFramework,
)
from openprocurement.framework.core.procedure.models.framework import (
    PatchFramework as BasePatchFramework,
)
from openprocurement.framework.core.procedure.models.framework import (
    PostFramework as BasePostFramework,
)
from openprocurement.framework.core.procedure.models.organization import (
    PatchActiveProcuringEntity,
    PatchProcuringEntity,
    ProcuringEntity,
)
from openprocurement.framework.dps.constants import DPS_TYPE


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
