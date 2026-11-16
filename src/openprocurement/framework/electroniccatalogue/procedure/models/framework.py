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
    PatchActiveProcuringEntity as PatchActiveCentralProcuringEntity,
)
from openprocurement.framework.electroniccatalogue.constants import ElectronicCatalogueFrameworkType
from openprocurement.framework.electroniccatalogue.procedure.models.organization import (
    CentralProcuringEntity,
    PatchCentralProcuringEntity,
)


class PostFramework(BasePostFramework):
    frameworkType: ElectronicCatalogueFrameworkType = FrameworkType.ELECTRONIC_CATALOGUE
    procuringEntity: CentralProcuringEntity


class PatchFramework(BasePatchFramework):
    procuringEntity: PatchCentralProcuringEntity | None = None


class Framework(BaseFramework):
    frameworkType: ElectronicCatalogueFrameworkType = FrameworkType.ELECTRONIC_CATALOGUE
    procuringEntity: CentralProcuringEntity


class PatchActiveFramework(BasePatchActiveFramework):
    procuringEntity: PatchActiveCentralProcuringEntity | None = None
