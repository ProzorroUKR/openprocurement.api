from schematics.types import StringType

from openprocurement.api.procedure.types import ModelType
from openprocurement.framework.arma.constants import ARMA_TYPE
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


class PostFramework(BasePostFramework):
    frameworkType = StringType(default=ARMA_TYPE)
    procuringEntity = ModelType(ProcuringEntity, required=True)


class PatchFramework(BasePatchFramework):
    procuringEntity = ModelType(PatchProcuringEntity)


class Framework(BaseFramework):
    frameworkType = StringType(default=ARMA_TYPE)
    procuringEntity = ModelType(ProcuringEntity, required=True)


class PatchActiveFramework(BasePatchActiveFramework):
    procuringEntity = ModelType(PatchActiveProcuringEntity)
