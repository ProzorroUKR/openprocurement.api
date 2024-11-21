from schematics.types import StringType

from openprocurement.api.procedure.types import ModelType
from openprocurement.framework.core.procedure.models.agreement import (
    Agreement as BaseAgreement,
)
from openprocurement.framework.core.procedure.models.organization import ProcuringEntity
from openprocurement.framework.ifi.constants import IFI_TYPE


class Agreement(BaseAgreement):
    agreementType = StringType(default=IFI_TYPE)
    procuringEntity = ModelType(ProcuringEntity, required=True)
