from datetime import timedelta

from openprocurement.api.constants_env import (
    AWARD_NOTICE_DOC_REQUIRED_FROM,
    NEW_ARTICLE_17_CRITERIA_REQUIRED,
    NEW_DEFENSE_COMPLAINTS_FROM,
    NEW_DEFENSE_COMPLAINTS_TO,
    QUALIFICATION_AFTER_COMPLAINT_FROM,
    REQ_RESPONSE_VALUES_VALIDATION_FROM,
)
from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import error_handler, raise_operation_error
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.contracting import add_contracts, append_contracts_cancelled
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.utils import (
    tender_created_after,
    tender_created_before,
    tender_created_in,
)
from openprocurement.tender.core.procedure.validation import (
    validate_doc_type_required,
    validate_econtract_fields_award,
    validate_items_required_fields,
    validate_req_response_values,
)
from openprocurement.tender.core.utils import calculate_tender_full_date


class AwardStateMixing:
    award_stand_still_working_days: bool = True
    sign_award_required: bool = True
    procurement_kinds_not_required_sign: tuple = ()
    award_has_period: bool = True
    items_delivery_required: bool = False
    items_unit_required: bool = True
    items_quantity_required: bool = True
    # procedures whose awards use `eligible` next to `qualified` (open family, cfaua, esco, arma, limited)
    award_has_eligible: bool = False
    # activation requires eligible=True (limited procedures only check it for the unsuccessful status)
    award_eligible_required_for_activation: bool = True
    # the unsuccessful status requires eligible=False as well (limited: only qualified=False)
    award_eligible_in_unsuccessful_rule: bool | None = None  # None = same as award_has_eligible
    # procedures without bids (limited) have no award items
    award_items_allowed: bool = True

    # --- status transition rules (procedure differences) ---
    # the next award is generated automatically after a status change (limited: awards are created manually)
    award_next_award_on_status_change: bool = True
    # complaintPeriod is set on the unsuccessful status (negotiation: only active awards get a complaint period)
    award_complaint_period_on_unsuccessful: bool = True
    # cancelling an award also cancels its complaints (bt/rfp)
    award_cancel_complaints_on_cancel: bool = True
    # open family/defense/CO: a satisfied complaint cancels all awards of the lot available for cancellation
    award_cancel_satisfied_complaint_lot_awards: bool = False
    # ... only the awards available for cancellation (negotiation: all of them)
    award_cancel_lot_awards_availability_check: bool = True
    # cfaselectionua: an award may become unsuccessful in active.qualification only after a cancelled award of the same bid
    award_unsuccessful_requires_cancelled_award_same_bid: bool = False
    # unsuccessful -> cancelled transition (cfaua overrides the whole transition instead of using these flags)
    award_unsuccessful_cancel_allowed: bool = True  # limited: forbidden
    # rfp: awards after the current one only, regardless of hasAwardingOrder
    award_unsuccessful_cancel_all_lot_awards: bool = True
    # openuadefense: tenders created in NEW_DEFENSE_COMPLAINTS_FROM..TO use the new complaints rules (complaintPeriod handling)
    award_new_defense_complaints_rules: bool = False
    # competitiveOrdering: the qualified/eligible rules depend on the tender creation date (NEW_ARTICLE_17_CRITERIA_REQUIRED)
    award_eligible_rules_by_creation_date: bool = False

    def is_new_defense_complaints(self):
        return self.award_new_defense_complaints_rules and tender_created_in(
            NEW_DEFENSE_COMPLAINTS_FROM, NEW_DEFENSE_COMPLAINTS_TO
        )

    def validate_award_patch(self, before, after):
        self.validate_award_qualified_eligible(after)
        self.validate_award_items_allowed(after)
        tender = get_tender()
        self.validate_cancellation_blocks(self.request, tender, lot_id=before.get("lotID"))
        self.validate_action_with_exist_inspector_review_request(lot_id=before.get("lotID"))
        validate_items_required_fields(
            self.request,
            after.get("items"),
            delivery=self.items_delivery_required,
            unit=self.items_unit_required,
            quantity=self.items_quantity_required,
        )
        if get_request_now() > REQ_RESPONSE_VALUES_VALIDATION_FROM:
            for resp in after.get("requirementResponses", []):
                validate_req_response_values(resp)

    def validate_award_qualified_eligible(self, award):
        """
        Replaces Award.validate_qualified / Award.validate_eligible model validators
        (eligible only takes part when award_has_eligible is True)
        """
        status = award.get("status")
        qualified = award.get("qualified")
        eligible = award.get("eligible")
        if self.award_eligible_rules_by_creation_date:
            self.validate_award_qualified_eligible_by_creation_date(award)
            return
        if not self.award_has_eligible and eligible is not None:
            # the field used to be absent on the models of these procedures
            raise_operation_error(self.request, "Rogue field", status=422, name="eligible")
        errors = []
        if status == "active":
            if not qualified:
                errors.append(("qualified", "Can't update award to active status with not qualified"))
            if self.award_has_eligible and self.award_eligible_required_for_activation and not eligible:
                errors.append(("eligible", "Can't update award to active status with not eligible"))
        elif status == "unsuccessful":
            with_eligible = self.award_eligible_in_unsuccessful_rule
            if with_eligible is None:
                with_eligible = self.award_has_eligible
            if (
                qualified is None
                or (with_eligible and eligible is None)
                or (qualified and (not with_eligible or eligible))
            ):
                errors.append(
                    (
                        "qualified",
                        "Can't update award to unsuccessful status when qualified/eligible isn't set to False",
                    )
                )
        if errors:
            for name, message in errors:
                self.request.errors.add("body", name, [message])
            self.request.errors.status = 422
            raise error_handler(self.request)

    def validate_award_qualified_eligible_by_creation_date(self, award):
        """competitiveOrdering: `active` requires qualified; the eligible rules depend on the tender creation date"""
        if award.get("status") == "active" and not award.get("qualified"):
            raise_operation_error(
                self.request,
                ["Can't update award to active status with not qualified"],
                status=422,
                name="qualified",
            )
        if tender_created_before(NEW_ARTICLE_17_CRITERIA_REQUIRED):
            if award["status"] == "active" and not award.get("eligible"):
                raise_operation_error(
                    self.request,
                    "Can't update award to active status with not eligible",
                    status=422,
                )
            if award["status"] == "unsuccessful" and (
                award.get("qualified") is None
                or award.get("eligible") is None
                or (award["qualified"] and award["eligible"])
            ):
                raise_operation_error(
                    self.request,
                    "Can't update award to unsuccessful status when qualified/eligible isn't set to False",
                    status=422,
                )
        else:
            if award.get("eligible") is not None:
                raise_operation_error(
                    self.request,
                    "Rogue field",
                    status=422,
                    name="eligible",
                )
            if award["status"] == "unsuccessful" and award.get("qualified") is not False:
                raise_operation_error(
                    self.request,
                    "Can't update award to unsuccessful status when qualified/eligible isn't set to False",
                    status=422,
                )

    def award_on_patch(self, before, award):
        self.validate_award_econtract_fields(award)
        if before["status"] != award["status"]:
            self.invalidate_review_requests(lot_id=award.get("lotID", ""))
            self.check_qualified_eligible_change(before, award)
            self.award_status_up(before["status"], award["status"], award)
        elif award["status"] == "pending":
            pass  # allowing to update award in pending status
        else:
            raise_operation_error(
                self.request,
                f"Can't update award in current ({before['status']}) status",
            )

    def check_qualified_eligible_change(self, before, award):
        if award["status"] == "cancelled" and (
            before.get("qualified") != award.get("qualified") or before.get("eligible") != award.get("eligible")
        ):
            raise_operation_error(
                self.request,
                f"Can't update qualified/eligible fields in award in ({award['status']}) status",
                status=422,
            )

    def validate_award_post(self, award):
        self.validate_award_items_allowed(award)

    def validate_award_items_allowed(self, award):
        if not self.award_items_allowed and award.get("items") is not None:
            raise_operation_error(self.request, "Rogue field", status=422, name="items")

    def award_on_post(self, award):
        self.validate_award_post(award)
        self.validate_award_econtract_fields(award)
        if self.award_has_period:
            award["period"] = {
                "startDate": get_request_now().isoformat(),
                "endDate": calculate_tender_full_date(
                    get_request_now(),
                    timedelta(days=self.award_period_duration),
                    tender=get_tender(),
                    working_days=True,
                ).isoformat(),
            }

    def award_status_up(self, before, after, award):
        assert before != after, "Statuses must be different"
        tender = get_tender()
        now = get_request_now().isoformat()

        if before == "pending" and after == "active":
            if (
                self.sign_award_required
                and tender_created_after(AWARD_NOTICE_DOC_REQUIRED_FROM)
                and tender.get("procuringEntity", {}).get("kind") not in self.procurement_kinds_not_required_sign
            ):
                validate_doc_type_required(award.get("documents", []), document_of="tender")
            self.award_status_up_from_pending_to_active(award, tender)

        elif before == "active" and after == "cancelled":
            self.award_status_up_from_active_to_cancelled(award, tender)

        elif before == "pending" and after == "unsuccessful":
            if (
                self.sign_award_required
                and tender_created_after(AWARD_NOTICE_DOC_REQUIRED_FROM)
                and tender.get("procuringEntity", {}).get("kind") not in self.procurement_kinds_not_required_sign
            ):
                validate_doc_type_required(award.get("documents", []), document_of="tender")
            self.award_status_up_from_pending_to_unsuccessful(award, tender)

        elif before == "unsuccessful" and after == "cancelled":
            self.award_status_up_from_unsuccessful_to_cancelled(award, tender)

        else:  # any other state transitions are forbidden
            raise_operation_error(self.request, f"Can't update award in current ({before}) status")

        # date updated when status updated
        award["date"] = now

    def award_status_up_from_pending_to_active(self, award, tender):
        if tender["config"]["hasAwardingOrder"] is False and not tender["config"].get("hasMultiSourcing"):
            self.check_active_awards(award, tender)
        self.set_award_complaint_period(award)
        if self.is_new_defense_complaints() and award.get("complaintPeriod"):
            # openuadefense: unsuccessful awards of the lot share the complaint period of the active one
            for i in tender.get("awards"):
                if i.get("lotID") == award.get("lotID") and i.get("status") == "unsuccessful":
                    i["complaintPeriod"] = award["complaintPeriod"]
        self.request.validated["contracts_added"] = add_contracts(self.request, award)
        if self.award_next_award_on_status_change:
            self.add_next_award()

    def award_status_up_from_active_to_cancelled(self, award, tender):
        if self.award_cancel_satisfied_complaint_lot_awards and any(
            i.get("status") == "satisfied" for i in award.get("complaints", "")
        ):
            # Cancel other same-lot awards available for cancellation
            for i in tender.get("awards", ""):
                if i["id"] == award["id"]:
                    continue
                if i.get("lotID") == award.get("lotID"):
                    if not self.award_cancel_lot_awards_availability_check or self.is_available_to_cancel_award(i):
                        self.cancel_award(i)
        elif self.award_cancel_complaints_on_cancel:
            self.set_award_complaints_cancelled(award)

        # Cancel the current award
        self.cancel_award(award)

        if self.award_next_award_on_status_change:
            self.add_next_award()

    def award_status_up_from_pending_to_unsuccessful(self, award, tender):
        if self.award_unsuccessful_requires_cancelled_award_same_bid and tender["status"] == "active.qualification":
            if not any(
                a["bid_id"] == award["bid_id"]
                and a["status"] == "cancelled"  # not need to check `a["id"] != award["id"]`
                for a in tender.get("awards", [])
            ):
                raise_operation_error(
                    self.request,
                    f"Can't update award status to {award['status']}, if tender status is {tender['status']}"
                    " and there is no cancelled award with the same bid_id",
                )
        if self.award_complaint_period_on_unsuccessful and not self.is_new_defense_complaints():
            self.set_award_complaint_period(award)
        if self.award_next_award_on_status_change:
            self.add_next_award()

    def award_status_up_from_unsuccessful_to_cancelled(self, award, tender):
        if not self.award_unsuccessful_cancel_allowed:
            raise_operation_error(self.request, "Can't update award in current (unsuccessful) status")
        if self.has_active_contract(award, tender):
            raise_operation_error(self.request, "Can't update award in current (unsuccessful) status")

        if tender["status"] == "active.awarded":
            # Go back to active.qualification status
            # because there is no active award anymore
            # for at least one of the lots
            tender["awardPeriod"].pop("endDate", None)
            self.get_change_tender_status_handler("active.qualification")(tender)

        if self.award_unsuccessful_cancel_all_lot_awards:
            # Cancel other same-lot awards available for cancellation
            for i in tender.get("awards", ""):
                if i["id"] == award["id"]:
                    continue
                if i.get("lotID") == award.get("lotID"):
                    if self.is_available_to_cancel_award(i):
                        self.cancel_award(i)
        else:
            if tender["config"]["hasAwardingOrder"]:
                # Cancel later same-lot awards (current award and next ones after it).
                # The current award is cancelled below,
                # then a new pending award is generated so qualification continues from it.
                lot_awards = [a for a in tender.get("awards") or [] if a.get("lotID") == award.get("lotID")]
                current_index = next(i for i, a in enumerate(lot_awards) if a["id"] == award["id"])
                for subsequent in lot_awards[current_index + 1 :]:
                    if self.award_cancel_complaints_on_cancel:
                        self.set_award_complaints_cancelled(subsequent)
                    self.cancel_award(subsequent)
            else:
                # It is intended to do nothing here
                # Only the current award should be cancelled
                # The new pending award will be generated instead of current one.
                pass

        # Cancel the current award
        if self.award_cancel_complaints_on_cancel:
            self.set_award_complaints_cancelled(award)
        self.cancel_award(award)

        # Generate a new pending award (or in some cases multiple awards if hasAwardingOrder is True)
        self.add_next_award()

    def cancel_multi_sourcing_pending_awards(self, award, tender):
        if not (tender["config"].get("hasMultiSourcing") and tender["config"].get("hasAwardingOrder")):
            return
        for i in tender.get("awards", ""):
            if i.get("lotID") == award.get("lotID") and i["status"] == "pending":
                self.cancel_award(i)

    @staticmethod
    def is_available_to_cancel_award(award):
        if tender_created_before(QUALIFICATION_AFTER_COMPLAINT_FROM):
            return award["status"] in ("pending", "active", "unsuccessful")
        return award["status"] in ("pending", "active")

    @staticmethod
    def check_active_awards(current_award, tender):
        for award in tender.get("awards", []):
            if (
                award["id"] != current_award["id"]
                and award["status"] == "active"
                and award.get("lotID") == current_award.get("lotID")
            ):
                raise_operation_error(
                    get_request(),
                    f"Can't activate award as tender already has "
                    f"active award{' for this lot' if current_award.get('lotID') else ''}",
                    status=422,
                    name="awards",
                )

    def cancel_award(self, award):
        if not self.is_new_defense_complaints():
            self.end_award_complaint_period(award)
        self.set_object_status(award, "cancelled")
        self.cancel_multi_sourcing_pending_awards(award, get_tender())
        contracts_cancelled = self.set_award_contracts_cancelled(award)
        append_contracts_cancelled(self.request, contracts_cancelled)

    # helpers
    @classmethod
    def set_award_contracts_cancelled(cls, award):
        tender = get_tender()
        contracts_cancelled = []
        for contract in tender.get("contracts", tuple()):
            if contract["awardID"] == award["id"]:
                if contract["status"] != "active":
                    cls.set_object_status(contract, "cancelled")
                    contracts_cancelled.append(contract)
                else:
                    raise_operation_error(get_request(), "Can't cancel award contract in active status")
        return contracts_cancelled

    @classmethod
    def set_award_complaints_cancelled(cls, award):
        for complaint in award.get("complaints", ""):
            if complaint["status"] not in ("invalid", "resolved", "declined"):
                cls.set_object_status(complaint, "cancelled")
                complaint["cancellationReason"] = "cancelled"
                complaint["dateCanceled"] = get_request_now().isoformat()

    def set_award_complaint_period(self, award):
        tender = get_tender()
        award_complain_duration = tender["config"]["awardComplainDuration"]
        if award_complain_duration > 0:
            award["complaintPeriod"] = {
                "startDate": get_request_now().isoformat(),
                "endDate": calculate_tender_full_date(
                    get_request_now(),
                    timedelta(days=award_complain_duration),
                    tender=tender,
                    working_days=self.award_stand_still_working_days,
                    calendar=self.calendar,
                ).isoformat(),
            }

    def end_award_complaint_period(self, award):
        now = get_request_now().isoformat()
        period = award.get("complaintPeriod")
        if period and (not period.get("endDate") or period["endDate"] > now):
            period["endDate"] = now

    def validate_award_econtract_fields(self, award):
        tender = self.request.validated["tender"]
        validate_econtract_fields_award(self.request, tender, award)

    @staticmethod
    def has_active_contract(current_award, tender):
        awards_ids = []
        for award in tender.get("awards", []):
            if tender.get("lots") and award["lotID"] != current_award["lotID"]:
                continue
            awards_ids.append(award["id"])
        for contract in tender.get("contracts", []):
            if contract["awardID"] in awards_ids:
                if contract["status"] == "active":
                    return True
        return False


# example use
class AwardState(AwardStateMixing, TenderState):
    pass
