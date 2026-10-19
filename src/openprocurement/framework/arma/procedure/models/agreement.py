from schematics.types import StringType

from openprocurement.api.procedure.types import ModelType
from openprocurement.framework.arma.constants import ARMA_TYPE
from openprocurement.framework.core.procedure.models.agreement import (
    Agreement as BaseAgreement,
)
from openprocurement.framework.core.procedure.models.organization import ProcuringEntity


class Agreement(BaseAgreement):
    agreementType = StringType(default=ARMA_TYPE)
    procuringEntity = ModelType(ProcuringEntity, required=True)
