from openprocurement.api.constants import AgreementType
from openprocurement.framework.core.procedure.models.agreement import (
    Agreement as BaseAgreement,
)
from openprocurement.framework.core.procedure.models.organization import ProcuringEntity
from openprocurement.framework.dps.constants import DPSAgreementType


class Agreement(BaseAgreement):
    agreementType: DPSAgreementType = AgreementType.DYNAMIC_PURCHASING_SYSTEM
    procuringEntity: ProcuringEntity
