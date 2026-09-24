from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.openuadefense.constants import WORKING_DAYS


class SimpleDefenseAwardState(AwardStateMixing, TenderState):
    award_stand_still_working_days: bool = True
    items_delivery_required: bool = True
    award_new_defense_complaints_rules = True
    award_cancel_lot_awards_on_satisfied_complaint = True
    generate_award_milestones = False
    calendar = WORKING_DAYS
    tender_new_defense_complaints_rules = True
    tender_lots_awarding_event_requires_stand_still = True
    award_has_eligible: bool = False
