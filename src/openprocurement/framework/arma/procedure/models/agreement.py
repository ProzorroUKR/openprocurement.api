from openprocurement.api.constants import AgreementType
from openprocurement.framework.arma.constants import ARMAAgreementType
from openprocurement.framework.core.procedure.models.agreement import (
    Agreement as BaseAgreement,
)
from openprocurement.framework.core.procedure.models.organization import ProcuringEntity


class Agreement(BaseAgreement):
    agreementType: ARMAAgreementType = AgreementType.ASSET_RECOVERY_MANAGEMENT_AGENCY
    procuringEntity: ProcuringEntity
