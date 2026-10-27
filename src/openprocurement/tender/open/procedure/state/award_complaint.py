from openprocurement.tender.core.procedure.state.award_complaint import (
    AwardComplaintStateMixin,
)
from openprocurement.tender.open.procedure.state.tender import (
    AboveThresholdEUTenderState,
    AboveThresholdTenderState,
    AboveThresholdUATenderState,
    COTenderState,
    DefenseTenderState,
    OpenTenderingTenderState,
    SimpleDefenseTenderState,
)


class AboveThresholdAwardComplaintState(AwardComplaintStateMixin, AboveThresholdTenderState):
    pass


class AboveThresholdUAAwardComplaintState(AwardComplaintStateMixin, AboveThresholdUATenderState):
    pass


class AboveThresholdEUAwardComplaintState(AwardComplaintStateMixin, AboveThresholdEUTenderState):
    pass


class DefenseAwardComplaintState(AwardComplaintStateMixin, DefenseTenderState):
    pass


class SimpleDefenseAwardComplaintState(AwardComplaintStateMixin, SimpleDefenseTenderState):
    pass


class COAwardComplaintState(AwardComplaintStateMixin, COTenderState):
    pass


class OpenTenderingAwardComplaintState(AwardComplaintStateMixin, OpenTenderingTenderState):
    pass
