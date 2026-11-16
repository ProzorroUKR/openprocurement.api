from typing import Literal

from openprocurement.api.constants import AgreementType, FrameworkType

ARMAFrameworkType = Literal[FrameworkType.ASSET_RECOVERY_MANAGEMENT_AGENCY]  # type: ignore[valid-type]


ARMAAgreementType = Literal[AgreementType.ASSET_RECOVERY_MANAGEMENT_AGENCY]  # type: ignore[valid-type]
