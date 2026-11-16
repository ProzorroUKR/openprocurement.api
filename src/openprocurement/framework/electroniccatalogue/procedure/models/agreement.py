from openprocurement.api.constants import AgreementType
from openprocurement.framework.core.procedure.models.agreement import (
    Agreement as BaseAgreement,
)
from openprocurement.framework.electroniccatalogue.constants import ElectronicCatalogueAgreementType
from openprocurement.framework.electroniccatalogue.procedure.models.organization import (
    CentralProcuringEntity,
)


class Agreement(BaseAgreement):
    agreementType: ElectronicCatalogueAgreementType = AgreementType.ELECTRONIC_CATALOGUE
    procuringEntity: CentralProcuringEntity
