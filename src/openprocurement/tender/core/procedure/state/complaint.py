from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.utils import tender_created_after_2020_rules, dt_from_iso, is_item_owner
from openprocurement.tender.core.procedure.models.complaint import (
    DraftPatchComplaint,
    CancellationPatchComplaint,
    BotPatchComplaint,
    TendererActionPatchComplaint,
    TendererResolvePatchComplaint,
    ReviewPatchComplaint,
    AdministratorPatchComplaint,
)
from openprocurement.tender.core.constants import (
    COMPLAINT_AMOUNT_RATE, COMPLAINT_MIN_AMOUNT, COMPLAINT_MAX_AMOUNT,
    COMPLAINT_ENHANCED_AMOUNT_RATE, COMPLAINT_ENHANCED_MIN_AMOUNT, COMPLAINT_ENHANCED_MAX_AMOUNT,
)
from openprocurement.tender.core.utils import restrict_value_to_bounds, round_up_to_ten
from openprocurement.api.utils import get_uah_amount_from_value
from logging import getLogger
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.context import get_now
from datetime import timedelta


LOGGER = getLogger(__name__)


class ComplaintState(TenderState):
    tender_complaint_submit_time = timedelta(days=4)
    create_allowed_tender_statuses = ("active.tendering",)
    update_allowed_tender_statuses = ("active.tendering",)

    # POST
    def validate_complaint_on_post(self, complaint):
        tender = get_tender()
        self.validate_create_allowed_tender_status()
        self.validate_lot_status()
        self.validate_tender_in_complaint_period(tender)

        self.validate_add_complaint_with_tender_cancellation_in_pending(tender)
        self.validate_add_complaint_with_lot_cancellation_in_pending(tender, complaint)

    def complaint_on_post(self, complaint):
        tender = get_tender()
        if tender_created_after_2020_rules():
            amount = self.get_complaint_amount(tender, complaint)
            complaint["value"] = dict(amount=round_up_to_ten(amount), currency="UAH")

        for doc in complaint.get("documents", ""):
            doc["author"] = "complaint_owner"

        self.always(tender)

    def validate_create_allowed_tender_status(self):
        if self.create_allowed_tender_statuses:
            tender = get_tender()
            if tender["status"] not in self.create_allowed_tender_statuses:
                raise_operation_error(
                    self.request,
                    f"Can't add complaint in current ({tender['status']}) tender status",
                )

    def validate_update_allowed_tender_status(self):
        if self.update_allowed_tender_statuses:
            tender = get_tender()
            if tender["status"] not in self.update_allowed_tender_statuses:
                raise_operation_error(
                    self.request,
                    f"Can't update complaint in current ({tender['status']}) tender status",
                )

    # PATCH
    def validate_complaint_on_patch(self, before, complaint):
        # validate forbidden for update fields
        for k in ("id", "scheme", "legalName"):
            if before["author"]["identifier"][k] != complaint["author"]["identifier"][k]:
                raise_operation_error(
                    self.request,
                    f"Can't change complaint author {k}",
                )
        self.validate_lot_status()

        # auth role action scenario
        _, handler = self.get_patch_action_model_and_handler()
        handler(complaint)

    def get_patch_data_model(self):
        model, _ = self.get_patch_action_model_and_handler()
        return model

    def get_patch_action_model_and_handler(self):
        request = self.request
        tender = get_tender()
        new_rules = tender_created_after_2020_rules()
        auth_role = request.authenticated_role
        current_complaint = request.validated["complaint"]
        status = current_complaint["status"]
        request_data = request.json["data"]
        new_status = request_data.get("status") or status

        self.validate_update_allowed_tender_status()

        def empty_handler(_):
            pass

        if auth_role == "bots":
            if new_rules and status == "draft" and new_status in ("pending", "mistaken"):
                if new_status == "mistaken":
                    def handler(complaint):
                        complaint["rejectReason"] = "incorrectPayment"
                    return BotPatchComplaint, handler
                elif new_status == "pending":
                    def handler(complaint):
                        complaint["dateSubmitted"] = get_now().isoformat()
                    return BotPatchComplaint, handler
            else:
                raise_operation_error(
                    self.request,
                    f"Can't update complaint from {status} to {new_status} status"
                )
        elif auth_role == "complaint_owner":
            if (
                new_status == "cancelled"
                and status == "draft"
                and not new_rules
            ):
                def handler(complaint):
                    complaint["dateCanceled"] = get_now().isoformat()
                return CancellationPatchComplaint, handler
            elif (
                new_rules
                and status == "draft"
                and new_status == "mistaken"
            ):
                def handler(complaint):
                    complaint["rejectReason"] = "cancelledByComplainant"
                return DraftPatchComplaint, handler
            elif (
                status in ["pending", "accepted"]
                and new_status == "stopping"
                and not new_rules
            ):
                def handler(complaint):
                    complaint["dateCanceled"] = get_now().isoformat()
                return CancellationPatchComplaint, handler
            elif (
                status == "draft"
                and new_status == status
            ):
                return DraftPatchComplaint, empty_handler
            elif (
                tender["status"] == "active.tendering"
                and status == "draft"
                and new_status == "pending"
                and not new_rules
            ):
                def handler(complaint):
                    self.validate_tender_in_complaint_period(tender)
                    complaint["dateSubmitted"] = get_now().isoformat()
                return DraftPatchComplaint, handler
            else:
                raise_operation_error(
                    self.request,
                    f"Can't update complaint from {status} to {new_status} status"
                )

        elif auth_role == "tender_owner":
            if status == "satisfied" and new_status == status:
                return TendererResolvePatchComplaint, empty_handler
            elif (
                status == "satisfied"
                and request_data.get("tendererAction", current_complaint.get("tendererAction"))
                and new_status == "resolved"
            ):
                return TendererResolvePatchComplaint, empty_handler
            elif status in ["pending", "accepted"]:
                return TendererActionPatchComplaint, empty_handler
            else:
                raise_operation_error(self.request, "Forbidden")

        elif auth_role == "aboveThresholdReviewers":
            if (
                status in ["pending", "accepted", "stopping"]
                and new_status == status
            ):
                return ReviewPatchComplaint, empty_handler
            elif (
                status in ["pending", "stopping"]
                and (
                    (not new_rules and new_status in ["invalid", "mistaken"])
                    or (new_status == "invalid")
                )
            ):
                def handler(complaint):
                    complaint["dateDecision"] = get_now().isoformat()
                    complaint["acceptance"] = False
                return ReviewPatchComplaint, handler
            elif status == "pending" and new_status == "accepted":
                def handler(complaint):
                    complaint["dateAccepted"] = get_now().isoformat()
                    complaint["acceptance"] = True
                return ReviewPatchComplaint, handler
            elif (
                status in ["accepted", "stopping"]
                and new_status == "declined"
            ):
                return ReviewPatchComplaint, self.reviewers_declined_handler
            elif (
                status in ["accepted", "stopping"]
                and new_status == "satisfied"
            ):
                return ReviewPatchComplaint, self.reviewers_satisfied_handler
            elif (
                (not new_rules and status in ["pending", "accepted", "stopping"])
                or (new_rules and status == "accepted")
                and new_status == "stopped"
            ):
                def handler(complaint):
                    complaint["dateDecision"] = get_now().isoformat()
                    complaint["dateCanceled"] = complaint.get("dateCanceled") or get_now().isoformat()

                return ReviewPatchComplaint, handler
            else:
                raise_operation_error(
                    self.request,
                    f"Can't update complaint from {status} to {new_status} status"
                )
        elif auth_role == "Administrator":
            return AdministratorPatchComplaint, empty_handler
        else:
            raise_operation_error(request, f"Cannot perform any action on complaint as {auth_role}")

    def reviewers_satisfied_handler(self, complaint):
        complaint["dateDecision"] = get_now().isoformat()

    def reviewers_declined_handler(self, complaint):
        complaint["dateDecision"] = get_now().isoformat()

    def complaint_on_patch(self, before, complaint):
        if before["status"] != complaint["status"]:
            self.complaint_status_up(before["status"], complaint["status"], complaint)

        self.always(get_tender())

    def complaint_status_up(self, before, after, complaint):
        complaint["date"] = get_now().isoformat()
        # if before != "pending" and after != "cancelled":
        #     raise_operation_error(self.request, "Can't update qualification status")

    def validate_tender_in_complaint_period(self, tender):
        complaint_submit_time = self.tender_complaint_submit_time
        if get_now() > dt_from_iso(tender["complaintPeriod"]["endDate"]):
            raise_operation_error(
                self.request,
                "Can submit complaint not later than {duration.days} "
                "full calendar days before tenderPeriod ends".format(
                    duration=complaint_submit_time
                ),
            )

    def validate_lot_status(self):
        pass

    def get_related_lot_obj(self, tender, complaint):
        if related_lot := complaint.get("relatedLot"):
            for lot in tender.get("lots"):
                if lot["id"] == related_lot:
                    return lot

    def get_complaint_amount(self, tender, complaint):
        related_lot = self.get_related_lot_obj(tender, complaint)
        value = related_lot["value"] if related_lot else tender["value"]
        base_amount = get_uah_amount_from_value(
            self.request, value, {"complaint_id": complaint["id"]}
        )
        if tender["status"] == "active.tendering":
            amount = restrict_value_to_bounds(
                base_amount * COMPLAINT_AMOUNT_RATE,
                COMPLAINT_MIN_AMOUNT,
                COMPLAINT_MAX_AMOUNT
            )
        else:
            amount = restrict_value_to_bounds(
                base_amount * COMPLAINT_ENHANCED_AMOUNT_RATE,
                COMPLAINT_ENHANCED_MIN_AMOUNT,
                COMPLAINT_ENHANCED_MAX_AMOUNT
            )
        return amount

    def validate_add_complaint_with_tender_cancellation_in_pending(self, tender):
        if tender_created_after_2020_rules():
            if any(
                i.get("status") == "pending" and not i.get("relatedLot")
                for i in tender.get("cancellations", "")
            ):
                raise_operation_error(self.request, "Can't add complaint if tender have cancellation in pending status")

    def validate_add_complaint_with_lot_cancellation_in_pending(self, tender, complaint):
        if tender_created_after_2020_rules():
            lot = self.get_related_lot_obj(tender, complaint)
            if lot:
                if any(
                    i.get("status") == "pending" and i.get("relatedLot") == lot["id"]
                    for i in tender.get("cancellations", "")
                ):
                    raise_operation_error(
                        self.request,
                        "Can't add complaint with 'pending' lot cancellation",
                    )
