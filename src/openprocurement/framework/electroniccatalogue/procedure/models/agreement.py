from schematics.types import StringType

from openprocurement.api.procedure.types import ModelType
from openprocurement.framework.core.procedure.models.agreement import (
    Agreement as BaseAgreement,
)
from openprocurement.framework.electroniccatalogue.constants import (
    ELECTRONIC_CATALOGUE_TYPE,
)
from openprocurement.framework.electroniccatalogue.procedure.models.organization import (
    CentralProcuringEntity,
)


class Agreement(BaseAgreement):
    agreementType = StringType(default=ELECTRONIC_CATALOGUE_TYPE)
    procuringEntity = ModelType(CentralProcuringEntity, required=True)
