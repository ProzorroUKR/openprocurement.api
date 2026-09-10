from openprocurement.tender.openuadefense.procedure.state.award import (
    AwardState as DefenseAwardState,
)


class SimpleDefenseAwardState(DefenseAwardState):
    award_has_eligible: bool = False
