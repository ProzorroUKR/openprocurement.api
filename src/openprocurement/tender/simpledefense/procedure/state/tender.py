from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.openuadefense.constants import WORKING_DAYS


class SimpleDefenseTenderState(TenderState):
    calendar = WORKING_DAYS
    tender_new_defense_complaints_rules = True
    tender_lots_awarding_event_requires_stand_still = True
    generate_award_milestones = False
