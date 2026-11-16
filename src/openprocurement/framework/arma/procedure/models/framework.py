from openprocurement.api.constants import FrameworkType
from openprocurement.framework.arma.constants import ARMAFrameworkType
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
    frameworkType: ARMAFrameworkType = FrameworkType.ASSET_RECOVERY_MANAGEMENT_AGENCY
    procuringEntity: ProcuringEntity


class PatchFramework(BasePatchFramework):
    procuringEntity: PatchProcuringEntity | None = None


class Framework(BaseFramework):
    frameworkType: ARMAFrameworkType = FrameworkType.ASSET_RECOVERY_MANAGEMENT_AGENCY
    procuringEntity: ProcuringEntity


class PatchActiveFramework(BasePatchActiveFramework):
    procuringEntity: PatchActiveProcuringEntity | None = None
