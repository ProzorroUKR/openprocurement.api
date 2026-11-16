from typing import Literal

from openprocurement.api.constants import AgreementType, FrameworkType

DPSFrameworkType = Literal[FrameworkType.DYNAMIC_PURCHASING_SYSTEM]  # type: ignore[valid-type]


DPSAgreementType = Literal[AgreementType.DYNAMIC_PURCHASING_SYSTEM]  # type: ignore[valid-type]
