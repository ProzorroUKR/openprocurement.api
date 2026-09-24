from openprocurement.tender.core.procedure.state.award import AwardStateMixin
from openprocurement.tender.openuadefense.procedure.state.tender import (
    DefenseTenderState,
)


class DefenseAwardState(AwardStateMixin, DefenseTenderState):
    award_stand_still_working_days: bool = True
    items_delivery_required: bool = True
    award_new_defense_complaints_rules = True
