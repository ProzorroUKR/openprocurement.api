from openprocurement.api.context import get_request
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import get_tender_product, raise_operation_error
from openprocurement.tender.core.constants import CRITERION_LOCALIZATION
from openprocurement.tender.core.procedure.state.award import AwardStateMixin
from openprocurement.tender.core.procedure.utils import tender_created_after_2020_rules
from openprocurement.tender.core.procedure.validation import OPERATIONS
from openprocurement.tender.limited.constants import LOCALIZATION_LEVEL_REQUIREMENT_TITLE
from openprocurement.tender.limited.procedure.models.award import (
    LimitedAward,
    LimitedPatchAward,
    LimitedPostAward,
    ReportingAward,
    ReportingPatchAward,
    ReportingPostAward,
)
from openprocurement.tender.limited.procedure.state.tender import NegotiationTenderState


class ReportingAwardState(AwardStateMixin, NegotiationTenderState):
    award_post_data_model = ReportingPostAward
    award_patch_data_model = ReportingPatchAward
    award_data_model = ReportingAward

    award_status_change_waits_for_milestone_due_date = False
    award_eligible_required_for_activation: bool = False
    award_eligible_in_unsuccessful_rule: bool = False
    award_items_allowed: bool = False
    sign_award_required = False
    generate_award_milestones = False
    award_has_period = False
    award_next_award_on_status_change = False
    award_unsuccessful_cancel_allowed = False
    award_post_requires_active_lot = False
    award_post_allowed_tender_statuses = ("active",)
    award_patch_allowed_tender_statuses = ("active",)
    award_patch_requires_active_lot = False
    award_cancel_lot_awards_on_satisfied_complaint = False
    award_stand_still_working_days = True

    def validate_award_post_content(self, award):
        self.validate_create_new_award(award)
        super().validate_award_post_content(award)

    def award_status_up_from_pending_to_active(self, award, tender):
        self.validate_items_product_localization_exception(award, tender)
        super().award_status_up_from_pending_to_active(award, tender)

    def validate_items_product_localization_exception(self, award, tender):
        answered_items = self.get_localization_level_answered_items(award, tender)

        for item in answered_items:
            category_id = item.get("category")
            product_id = item.get("product")

            if not category_id:
                continue

            if not product_id:
                raise_operation_error(
                    self.request,
                    [{"product": ["This field is required."]}],
                    status=422,
                    name="items",
                )

            get_tender_product(get_request(), product_id, related_category=category_id)

    @staticmethod
    def get_localization_level_answered_items(award: dict, tender: dict) -> list:
        requirement_response_ids = {response["requirement"]["id"] for response in award.get("requirementResponses", [])}

        answered_item_ids = set()
        for criteria in tender.get("criteria", []):
            if criteria.get("classification", {}).get("id") == CRITERION_LOCALIZATION:
                for group in criteria.get("requirementGroups", []):
                    for req in group.get("requirements", []):
                        if req["id"] in requirement_response_ids and req.get("title", "").strip() == (
                            LOCALIZATION_LEVEL_REQUIREMENT_TITLE
                        ):
                            answered_item_ids.add(criteria.get("relatedItem"))

        return [item for item in tender.get("items", []) if item["id"] in answered_item_ids]

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
    award_post_data_model = LimitedPostAward
    award_patch_data_model = LimitedPatchAward
    award_data_model = LimitedAward

    award_stand_still_working_days: bool = False
    sign_award_required = True
    award_complaint_period_on_unsuccessful = False
    award_cancel_lot_awards_on_satisfied_complaint = True
    award_post_lot_cancellation_pending_check = True

    def validate_award_post_content(self, award):
        self.validate_award_lot_cancellation(award)
        super().validate_award_post_content(award)

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
