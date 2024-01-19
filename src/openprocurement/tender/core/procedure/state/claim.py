from openprocurement.api.validation import validate_json_data
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.utils import calculate_tender_business_date
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.core.procedure.state.complaint import BaseComplaintStateMixin
from openprocurement.tender.core.procedure.models.claim import (
    ClaimOwnerClaimDraft,
    ClaimOwnerClaimCancellation,
    ClaimOwnerClaimSatisfy,
    TenderOwnerClaimAnswer,
)
from logging import getLogger
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.context import get_now
from datetime import datetime, timedelta


LOGGER = getLogger(__name__)


class ClaimStateMixin(BaseComplaintStateMixin):
    tender_claim_submit_time = timedelta(days=3)
    create_allowed_tender_statuses = ("active.tendering",)
    update_allowed_tender_statuses = (
        "active.tendering",
        "active.auction",
        "active.qualification",
        "active.awarded",
    )
    patch_as_complaint_owner_tender_statuses = ("active.tendering",)

    def claim_on_post(self, complaint):
        if complaint.get("status") == "claim":
            complaint["dateSubmitted"] = get_now().isoformat()

        for doc in complaint.get("documents", ""):
            doc["author"] = "complaint_owner"

        tender = get_tender()
        self.always(tender)

    def claim_on_patch(self, before, claim):
        if before["status"] != claim["status"]:
            self.claim_status_up(before["status"], claim["status"], claim)

    def claim_status_up(self, before, after, complaint):
        complaint["date"] = get_now().isoformat()
        if after == "answered":
            if not complaint.get("resolutionType"):
                raise_operation_error(
                    self.request,
                    ["This field is required."],
                    status=422,
                    location="body",
                    name="resolutionType"
                )

    def validate_claim_on_post(self, complaint):
        tender = get_tender()
        status = tender["status"]
        if status not in self.create_allowed_tender_statuses:
            raise_operation_error(
                self.request,
                f"Can't add complaint in current ({status}) tender status",
            )
        self.validate_lot_status()
        self.validate_tender_in_complaint_period(tender)
        self.validate_add_complaint_with_tender_cancellation_in_pending(tender)

        if complaint.get("status") == "claim":
            self.validate_submit_claim(complaint)

    def validate_tender_in_complaint_period(self, tender):
        enquiry_end = tender.get("enquiryPeriod", {}).get("endDate")
        if enquiry_end and get_now() > datetime.fromisoformat(enquiry_end):
            raise_operation_error(
                self.request,
                "Can submit complaint only in enquiryPeriod",
            )

    def validate_lot_status(self):
        pass

    def validate_claim_on_patch(self, before, claim):
        # auth role action scenario
        _, handler = self.get_patch_action_model_and_handler()
        handler(claim)

    def get_patch_data_model(self):
        model, _ = self.get_patch_action_model_and_handler()
        return model

    def get_patch_action_model_and_handler(self):
        request = self.request
        auth_role = request.authenticated_role
        tender = get_tender()
        tender_status = tender["status"]
        validated_claim = request.validated["claim"]
        status = validated_claim["status"]
        request_data = validate_json_data(request)
        new_status = request_data.get("status") or status

        # TODO: merge these two checks with the scenarios
        if tender_status not in self.update_allowed_tender_statuses:
            raise_operation_error(
                self.request,
                f"Can't update complaint in current ({tender_status}) tender status",
            )

        self.validate_lot_status()

        if status not in ("draft", "claim", "answered"):
            raise_operation_error(
                self.request,
                f"Can't update complaint in current ({status}) status"
            )

        def empty_handler(_):
            pass
        if auth_role == "complaint_owner":
            if (
                new_status == "cancelled"
                and status in ["draft", "claim", "answered"]
            ):
                def handler(claim):
                    claim["dateCanceled"] = get_now().isoformat()
                return ClaimOwnerClaimCancellation, handler
            elif (
                tender_status in self.patch_as_complaint_owner_tender_statuses
                and status == "draft"
                and new_status == status
            ):
                return ClaimOwnerClaimDraft, empty_handler
            elif (
                tender_status in self.patch_as_complaint_owner_tender_statuses
                and status == "draft"
                and new_status == "claim"
            ):
                def handler(claim):
                    self.validate_submit_claim(claim)
                    claim["dateSubmitted"] = get_now().isoformat()
                return ClaimOwnerClaimDraft, handler

            elif status == "answered" and new_status == status:
                return ClaimOwnerClaimSatisfy, empty_handler
            elif (
                status == "answered"
                and new_status == "resolved"
                and self.validate_satisfied(
                    request_data.get("satisfied", validated_claim.get("satisfied"))
                )
            ):
                return ClaimOwnerClaimSatisfy, empty_handler
            else:
                raise_operation_error(
                    self.request,
                    f"Can't update complaint from {status} to {new_status} status"
                )
        elif auth_role == "tender_owner":
            if status == "claim" and new_status == status:
                def handler(claim):
                    self.validate_tender_owner_update_claim_time()
                return TenderOwnerClaimAnswer, handler
            elif status == "claim" and new_status == "answered":
                def handler(claim):
                    self.validate_tender_owner_update_claim_time()
                    if not claim.get("resolutionType"):
                        raise_operation_error(
                            self.request,
                            ["This field is required."],
                            status=422,
                            location="body",
                            name="resolutionType"

                        )
                    if len(claim.get("resolution", "")) < 20:
                        raise_operation_error(self.request, "Can't update complaint: resolution too short")
                    claim["dateAnswered"] = get_now().isoformat()

                return TenderOwnerClaimAnswer, handler
            else:
                raise_operation_error(
                    self.request,
                    f"Can't update complaint from {status} to {new_status} status"
                )
        else:
            raise_operation_error(request, f"Cannot perform any action on complaint as {auth_role}")

    def validate_submit_claim(self, claim):
        request = self.request
        tender = request.validated["tender"]
        claim_submit_time = self.tender_claim_submit_time
        tender_end = tender.get("tenderPeriod", {}).get("endDate")
        claim_end_date = calculate_tender_business_date(dt_from_iso(tender_end), -claim_submit_time, tender)
        if get_now() > claim_end_date:
            raise_operation_error(
                request,
                f"Can submit claim not later than {claim_submit_time.days} full calendar days before tenderPeriod ends"
            )

    def validate_tender_owner_update_claim_time(self):
        request = self.request
        tender = request.validated["tender"]
        clarifications_until = tender.get("enquiryPeriod", {}).get("clarificationsUntil")
        if clarifications_until and get_now() > datetime.fromisoformat(clarifications_until):
            raise_operation_error(self.request, "Can update complaint only before enquiryPeriod.clarificationsUntil")

    @staticmethod
    def validate_satisfied(satisfied):
        return satisfied is True


class TenderClaimState(ClaimStateMixin, TenderState):
    pass