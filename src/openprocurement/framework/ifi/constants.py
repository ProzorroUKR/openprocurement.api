from typing import Literal

from openprocurement.api.constants import AgreementType, FrameworkType

IFIFrameworkType = Literal[FrameworkType.INTERNATIONAL_FINANCIAL_INSTITUTIONS]  # type: ignore[valid-type]


IFIAgreementType = Literal[AgreementType.INTERNATIONAL_FINANCIAL_INSTITUTIONS]  # type: ignore[valid-type]
