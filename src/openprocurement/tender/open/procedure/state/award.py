from openprocurement.api.constants import WORKING_DAYS_WITH_WORKING_WEEKENDS
from openprocurement.tender.core.procedure.state.award import AwardStateMixin
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.open.procedure.state.tender import (
    AboveThresholdTenderState,
    AboveThresholdUATenderState,
    BelowThresholdTenderState,
    COTenderState,
    DefenseTenderState,
    RFPTenderState,
)


class AboveThresholdAwardState(AwardStateMixin, AboveThresholdTenderState):
    items_delivery_required: bool = True


class AboveThresholdUAAwardState(AwardStateMixin, AboveThresholdUATenderState):
    items_delivery_required: bool = True


class DefenseAwardState(AwardStateMixin, DefenseTenderState):
    award_stand_still_working_days: bool = True
    items_delivery_required: bool = True
    award_new_defense_complaints_rules = True


class SimpleDefenseAwardState(AwardStateMixin, TenderState):
    award_stand_still_working_days: bool = True
    items_delivery_required: bool = True
    award_new_defense_complaints_rules = True
    generate_award_milestones = False
    calendar = WORKING_DAYS_WITH_WORKING_WEEKENDS
    tender_new_defense_complaints_rules = True
    tender_lots_awarding_event_requires_stand_still = True
    award_has_eligible: bool = False


class COAwardState(AwardStateMixin, COTenderState):
    items_delivery_required: bool = True
    award_eligible_rules_by_creation_date = True


class BelowThresholdAwardState(AwardStateMixin, BelowThresholdTenderState):
    award_cancel_claims_on_cancel = True
    award_cancel_lot_awards_on_satisfied_complaint = False
    award_has_eligible = False
    award_stand_still_working_days = True


class RFPAwardState(AwardStateMixin, RFPTenderState):
    award_cancel_claims_on_cancel = True
    sign_award_required = False
    award_unsuccessful_cancel_all_lot_awards = False  # awards after the current one only
    award_cancel_lot_awards_on_satisfied_complaint = False
    award_has_eligible = False
    award_stand_still_working_days = True
