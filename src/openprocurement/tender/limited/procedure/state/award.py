from openprocurement.api.constants_env import NEGOTIATION_VAT_NOT_INCLUDED_VALIDATION_FROM
from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.limited.procedure.state.tender import NegotiationTenderState
from openprocurement.tender.limited.procedure.state.tender_details import (
    cause_scheme_requires_vat_not_included,
)


class ReportingAwardState(AwardStateMixing, NegotiationTenderState):
    award_has_eligible: bool = True
    award_eligible_required_for_activation: bool = False
    award_eligible_in_unsuccessful_rule: bool = False
    award_items_allowed: bool = False
    sign_award_required = False
    generate_award_milestones = False
    award_has_period = False
    award_next_award_on_status_change = False
    award_unsuccessful_cancel_allowed = False


class NegotiationAwardState(ReportingAwardState):
    award_stand_still_working_days: bool = False
    sign_award_required = True
    award_complaint_period_on_unsuccessful = False
    award_cancel_complaints_on_cancel = False
    award_cancel_satisfied_complaint_lot_awards = True
    award_cancel_lot_awards_availability_check = False
    award_value_vat_not_included_from = NEGOTIATION_VAT_NOT_INCLUDED_VALIDATION_FROM

    @property
    def award_value_vat_not_included(self):
        return cause_scheme_requires_vat_not_included(get_tender())


class NegotiationQuickAwardState(NegotiationAwardState):
    pass
