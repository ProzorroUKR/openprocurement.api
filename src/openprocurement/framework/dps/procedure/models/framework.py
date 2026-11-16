from openprocurement.api.constants import FrameworkType
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
from openprocurement.framework.dps.constants import DPSFrameworkType


class PostFramework(BasePostFramework):
    frameworkType: DPSFrameworkType = FrameworkType.DYNAMIC_PURCHASING_SYSTEM
    procuringEntity: ProcuringEntity


class PatchFramework(BasePatchFramework):
    procuringEntity: PatchProcuringEntity | None = None


class Framework(BaseFramework):
    frameworkType: DPSFrameworkType = FrameworkType.DYNAMIC_PURCHASING_SYSTEM
    procuringEntity: ProcuringEntity


class PatchActiveFramework(BasePatchActiveFramework):
    procuringEntity: PatchActiveProcuringEntity | None = None
