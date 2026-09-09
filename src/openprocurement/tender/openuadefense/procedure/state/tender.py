from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.openuadefense.constants import WORKING_DAYS


class DefenseTenderStateAwardingMixing:
    tender_new_defense_complaints_rules = True
    tender_lots_awarding_event_requires_stand_still = True


class OpenUADefenseTenderState(DefenseTenderStateAwardingMixing, TenderState):
    block_complaint_status = ("pending", "accepted", "satisfied", "stopping")
    generate_award_milestones = False
    calendar = WORKING_DAYS
