from openprocurement.api.constants import WORKING_DAYS_WITH_WORKING_WEEKENDS
from openprocurement.tender.core.procedure.state.tender import TenderState


class SimpleDefenseTenderState(TenderState):
    calendar = WORKING_DAYS_WITH_WORKING_WEEKENDS
    tender_new_defense_complaints_rules = True
    tender_lots_awarding_event_requires_stand_still = True
    generate_award_milestones = False
