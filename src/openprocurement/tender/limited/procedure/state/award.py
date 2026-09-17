from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.core.procedure.utils import tender_created_after_2020_rules
from openprocurement.tender.core.procedure.validation import OPERATIONS
from openprocurement.tender.limited.procedure.state.tender import NegotiationTenderState


class ReportingAwardState(AwardStateMixing, NegotiationTenderState):
    award_status_change_waits_for_milestone_due_date = False
    award_has_eligible: bool = True
    award_eligible_required_for_activation: bool = False
    award_eligible_in_unsuccessful_rule: bool = False
    award_items_allowed: bool = False
    sign_award_required = False
    generate_award_milestones = False
    award_has_period = False
    award_next_award_on_status_change = False
    award_unsuccessful_cancel_allowed = False
    award_post_requires_active_lot = False

    def validate_award_post(self, award):
        self.validate_create_new_award(award)
        super().validate_award_post(award)

    def validate_create_new_award(self, award):
        tender = get_tender()
        if tender.get("awards"):
            last_status = tender["awards"][-1]["status"]
            if last_status in ("pending", "active"):
                raise_operation_error(
                    self.request,
                    f"Can't create new award while any ({last_status}) award exists",
                )


class NegotiationAwardState(ReportingAwardState):
    award_stand_still_working_days: bool = False
    sign_award_required = True
    award_complaint_period_on_unsuccessful = False
    award_cancel_lot_awards_on_satisfied_complaint = True

    def validate_award_post(self, award):
        self.validate_award_lot_cancellation(award)
        super().validate_award_post(award)

    def validate_award_patch(self, before, after):
        self.validate_award_lot_cancellation(before)
        self.validate_award_same_lot_id(after)
        super().validate_award_patch(before, after)

    def validate_create_new_award(self, award):
        tender = get_tender()
        if not tender.get("lots"):
            return super().validate_create_new_award(award)
        lot_id = award.get("lotID")
        awards = tender.get("awards", "")
        if any(lot_id == aw.get("lotID") for aw in awards if aw["status"] in ("pending", "active")):
            raise_operation_error(
                self.request,
                f"Can't create new award on lot while any ({awards[-1]['status']}) award exists",
            )

    def validate_award_lot_cancellation(self, award):
        if tender_created_after_2020_rules():
            return
        tender = get_tender()
        lot_id = award.get("lotID")
        if tender.get("lots") and any(c.get("relatedLot") == lot_id for c in tender.get("cancellations", "")):
            raise_operation_error(
                self.request,
                f"Can't {OPERATIONS.get(self.request.method)} award while cancellation for corresponding lot exists",
            )

    def validate_award_same_lot_id(self, award):
        tender = get_tender()
        lot_id = award.get("lotID")
        if lot_id and any(
            aw.get("lotID") == lot_id and aw["id"] != award["id"]
            for aw in tender.get("awards", "")
            if aw["status"] in ("pending", "active")
        ):
            raise_operation_error(
                self.request,
                "Another award is already using this lotID.",
                location="body",
                name="lotID",
            )


class NegotiationQuickAwardState(NegotiationAwardState):
    pass
