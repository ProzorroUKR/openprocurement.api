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
    PatchActiveProcuringEntity as PatchActiveCentralProcuringEntity,
)
from openprocurement.framework.electroniccatalogue.constants import (
    ELECTRONIC_CATALOGUE_TYPE,
)
from openprocurement.framework.electroniccatalogue.procedure.models.organization import (
    CentralProcuringEntity,
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
