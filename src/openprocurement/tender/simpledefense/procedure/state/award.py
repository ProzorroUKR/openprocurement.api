from openprocurement.api.constants import WORKING_DAYS_WITH_WORKING_WEEKENDS
from openprocurement.tender.core.procedure.state.award import AwardStateMixin
from openprocurement.tender.core.procedure.state.tender import TenderState


class SimpleDefenseAwardState(AwardStateMixin, TenderState):
    award_stand_still_working_days: bool = True
    items_delivery_required: bool = True
    award_new_defense_complaints_rules = True
    generate_award_milestones = False
    calendar = WORKING_DAYS_WITH_WORKING_WEEKENDS
    tender_new_defense_complaints_rules = True
    tender_lots_awarding_event_requires_stand_still = True
    award_has_eligible: bool = False
