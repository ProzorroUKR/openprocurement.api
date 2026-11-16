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
from openprocurement.framework.ifi.constants import IFIFrameworkType


class PostFramework(BasePostFramework):
    frameworkType: IFIFrameworkType = FrameworkType.INTERNATIONAL_FINANCIAL_INSTITUTIONS
    procuringEntity: ProcuringEntity


class PatchFramework(BasePatchFramework):
    procuringEntity: PatchProcuringEntity | None = None


class Framework(BaseFramework):
    frameworkType: IFIFrameworkType = FrameworkType.INTERNATIONAL_FINANCIAL_INSTITUTIONS
    procuringEntity: ProcuringEntity


class PatchActiveFramework(BasePatchActiveFramework):
    procuringEntity: PatchActiveProcuringEntity | None = None
