from openprocurement.api.constants import AgreementType
from openprocurement.framework.core.procedure.models.agreement import (
    Agreement as BaseAgreement,
)
from openprocurement.framework.core.procedure.models.organization import ProcuringEntity
from openprocurement.framework.ifi.constants import IFIAgreementType


class Agreement(BaseAgreement):
    agreementType: IFIAgreementType = AgreementType.INTERNATIONAL_FINANCIAL_INSTITUTIONS
    procuringEntity: ProcuringEntity
