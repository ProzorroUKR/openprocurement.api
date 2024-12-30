from schematics.types import StringType

from openprocurement.api.procedure.types import ModelType
from openprocurement.framework.core.procedure.models.agreement import (
    Agreement as BaseAgreement,
)
from openprocurement.framework.core.procedure.models.organization import ProcuringEntity
from openprocurement.framework.dps.constants import DPS_TYPE


class Agreement(BaseAgreement):
    agreementType = StringType(default=DPS_TYPE)
    procuringEntity = ModelType(ProcuringEntity, required=True)
