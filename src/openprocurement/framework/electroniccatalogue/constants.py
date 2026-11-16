from typing import Literal

from openprocurement.api.constants import AgreementType, FrameworkType

ElectronicCatalogueFrameworkType = Literal[FrameworkType.ELECTRONIC_CATALOGUE]  # type: ignore[valid-type]


ElectronicCatalogueAgreementType = Literal[AgreementType.ELECTRONIC_CATALOGUE]  # type: ignore[valid-type]
