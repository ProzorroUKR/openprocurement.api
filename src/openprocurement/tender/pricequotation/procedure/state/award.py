from openprocurement.tender.core.procedure.state.award import AwardStateMixin
from openprocurement.tender.pricequotation.procedure.state.tender import (
    PQTenderState,
)


class PQAwardState(AwardStateMixin, PQTenderState):
    award_status_change_waits_for_milestone_due_date = False
    procurement_kinds_not_required_sign = ("other",)  # in case when signing award will be required in the future
    award_cancel_lot_awards_on_satisfied_complaint = False
    award_has_eligible = False
    award_stand_still_working_days = True
