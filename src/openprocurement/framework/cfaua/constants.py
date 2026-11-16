from typing import Literal

from openprocurement.api.constants import AgreementType

MIN_BIDS_NUMBER = 3


CFAUAAgreementType = Literal[AgreementType.CLOSE_FRAMEWORK_AGREEMENT_UA]  # type: ignore[valid-type]
