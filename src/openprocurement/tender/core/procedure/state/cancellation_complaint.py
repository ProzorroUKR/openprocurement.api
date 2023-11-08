from openprocurement.tender.core.procedure.state.complaint import ComplaintStateMixin
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.utils import tender_created_after_2020_rules, dt_from_iso, is_item_owner
from openprocurement.tender.core.procedure.models.complaint import (
    DraftPatchCancellationComplaint,
    CancellationPatchComplaint,
    BotPatchComplaint,
    TendererActionPatchComplaint,
    TendererResolvePatchComplaint,
    ReviewPatchComplaint,
    AdministratorPatchComplaint,
)
from logging import getLogger
from openprocurement.tender.core.utils import calculate_tender_business_date
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.context import get_now
from datetime import timedelta


LOGGER = getLogger(__name__)


class CancellationComplaintStateMixin(ComplaintStateMixin):
    tender_complaint_submit_time = timedelta(days=4)
    update_allowed_tender_statuses = None

    def validate_complaint_on_post(self, complaint):
        tender = get_tender()

        self.validate_post_cancellation_complaint_permission()
        self.validate_cancellation_complaint_resolved(complaint)
        self.validate_tender_in_complaint_period(tender)
        self.validate_objection_related_item(complaint)

    def validate_objection_related_item(self, complaint):
        if objections := complaint.get("objections", []):
            cancellation = self.request.validated["cancellation"]
            for objection in objections:
                url_parts = objection.get("relatedItem", "").split("/")
                if url_parts[-1] != cancellation["id"]:
                    raise_operation_error(
                        self.request,
                        "Complaint's objection must relate to the same cancellation id as complaint relates to",
                        status=422,
                    )

    def validate_post_cancellation_complaint_permission(self):
        request = self.request
        if request.authenticated_role != "admins":
            tender = get_tender()
            if tender["status"] != "active.tendering":
                for bid in tender.get("bids", ""):
                    if is_item_owner(request, bid):
                        break
                else:
                    raise_operation_error(
                        request,
                        "Forbidden",
                        location="url",
                        name="permission"
                    )

    def validate_complaint_on_patch(self, before, complaint):
        # self.validate_cancellation_complaint_resolved(complaint)
        self.validate_objection_related_item(complaint)
        return super().validate_complaint_on_patch(before, complaint)

    def validate_cancellation_complaint_resolved(self, complaint):
        request = self.request
        cancellation = request.validated["cancellation"]
        if complaint.get("tendererAction") and cancellation.get("status") != "unsuccessful":
            raise_operation_error(
                request,
                "Complaint can't have tendererAction only if cancellation not in unsuccessful status",
                status=422,
            )

    def validate_tender_in_complaint_period(self, tender):
        request = self.request
        cancellation = request.validated["cancellation"]
        if cancellation.get("status") != "pending":
            raise_operation_error(
                request,
                "Complaint can be add only in pending status of cancellation",
                status=422,
            )

        complaint_period = cancellation.get("complaintPeriod")
        is_complaint_period = (
            dt_from_iso(complaint_period["startDate"]) <= get_now() <= dt_from_iso(complaint_period["endDate"])
            if complaint_period
            else False
        )
        if not is_complaint_period:
            raise_operation_error(
                request,
                "Complaint can't be add after finish of complaint period",
                status=422,
            )

    def get_patch_action_model_and_handler(self):
        request = self.request
        new_rules = tender_created_after_2020_rules()
        auth_role = request.authenticated_role
        current_complaint = request.validated["complaint"]
        status = current_complaint["status"]
        request_data = request.json["data"]
        new_status = request_data.get("status") or status

        # this one somewhat duplicates the checks below
        if status not in ("draft", "pending", "accepted", "satisfied", "stopping"):
            raise_operation_error(
                request,
                f"Can't update complaint in current ({status}) status",
            )

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
                status in ["pending", "accepted"]
                and new_status == "stopping"
            ):
                def handler(complaint):
                    complaint["dateCanceled"] = get_now().isoformat()
                return CancellationPatchComplaint, handler
            elif (
                status == "draft"
                and new_status == status
            ):
                return DraftPatchCancellationComplaint, empty_handler
            elif(
                status == "draft"
                and new_status == "mistaken"
            ):
                def handler(complaint):
                    complaint["rejectReason"] = "cancelledByComplainant"

                return DraftPatchCancellationComplaint, handler

            elif (
                status == "draft"
                and new_status == "pending"
                and not new_rules
            ):
                def handler(complaint):
                    complaint["dateSubmitted"] = get_now().isoformat()
                return DraftPatchCancellationComplaint, handler

            else:
                raise_operation_error(
                    self.request,
                    f"Can't update complaint from {status} to {new_status} status as {auth_role}"
                )

        elif auth_role == "tender_owner":
            self.validate_cancellation_complaint_resolved(request_data)
            if (
                status == "satisfied"
                and request_data.get("tendererAction")
                and not current_complaint.get("tendererAction")
            ):
                def handler(complaint):
                    complaint["status"] = "resolved"
                    complaint["tendererActionDate"] = get_now().isoformat()
                    self.recalculate_tender_periods(complaint)

                return TendererResolvePatchComplaint, handler

            elif status == "satisfied" and new_status == status:
                return TendererResolvePatchComplaint, empty_handler

            elif status in ["pending", "accepted"] and new_status == "stopping":
                return TendererActionPatchComplaint, empty_handler
            else:
                raise_operation_error(
                    self.request,
                    f"Can't update complaint from {status} to {new_status} status"
                )

        elif auth_role == "aboveThresholdReviewers":
            if (
                status in ["pending", "accepted", "stopping"]
                and new_status == status
            ):
                return ReviewPatchComplaint, empty_handler
            elif (
                status in ["pending", "stopping"]
                and new_status == "invalid"
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
                and new_status in ["declined", "satisfied"]
            ):
                def handler(complaint):
                    complaint["dateDecision"] = get_now().isoformat()
                    if new_status == "satisfied":
                        self.on_satisfy_complaint_by_reviewer()

                return ReviewPatchComplaint, handler
            elif (
                status == "accepted"
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

    def on_satisfy_complaint_by_reviewer(self):
        pass

    def recalculate_tender_periods(self, complaint):
        tender = self.request.validated["tender"]
        cancellation = self.request.validated["cancellation"]
        tenderer_action_date = dt_from_iso(complaint["tendererActionDate"])

        tender_period = tender.get("tenderPeriod")
        tender_period_end = dt_from_iso(tender_period["endDate"])

        auction_period = tender.get("auctionPeriod")

        date = dt_from_iso(cancellation["complaintPeriod"]["startDate"])
        delta = (tenderer_action_date - date).days
        delta_plus = 1 if (tenderer_action_date - date).seconds > 3599 else 0
        delta += delta_plus
        delta = timedelta(days=1 if not delta else delta)

        if tender["status"] == "active.tendering" and tender.get("enquiryPeriod"):
            enquiry_period = tender.get("enquiryPeriod")
            enquiry_period_start = dt_from_iso(enquiry_period["startDate"])

            if enquiry_period_start < date <= tender_period_end:
                if enquiry_period_end := enquiry_period.get("endDate"):
                    enquiry_period["endDate"] = calculate_tender_business_date(
                        dt_from_iso(enquiry_period_end),
                        delta,
                        tender,
                    ).isoformat()
                if clarifications_until := enquiry_period.get("clarificationsUntil"):
                    enquiry_period["clarificationsUntil"] = calculate_tender_business_date(
                        dt_from_iso(clarifications_until),
                        delta,
                        tender,
                    ).isoformat()

                if tender_period_end:
                    tender_period["endDate"] = calculate_tender_business_date(
                        tender_period_end,
                        delta,
                        tender,
                    ).isoformat()

                if auction_period:
                    if auction_should_start := auction_period.get("shouldStartAfter"):
                        auction_period["shouldStartAfter"] = calculate_tender_business_date(
                            dt_from_iso(auction_should_start),
                            delta,
                            tender,
                        ).isoformat()

                    if auction_start := auction_period.get("startDate"):
                        auction_period["startDate"] = calculate_tender_business_date(
                            dt_from_iso(auction_start),
                            delta,
                            tender,
                        ).isoformat()

            elif auction_period and tender_period_end and auction_period.get("shouldStartAfter"):
                auction_should_start = dt_from_iso(auction_period["shouldStartAfter"])
                if tender_period_end < date <= auction_should_start:
                    auction_period["shouldStartAfter"] = calculate_tender_business_date(
                        auction_should_start,
                        delta,
                        tender,
                    ).isoformat()

                    if auction_start := auction_period.get("startDate"):
                        auction_period["startDate"] = calculate_tender_business_date(
                            dt_from_iso(auction_start),
                            delta,
                            tender,
                        ).isoformat()

    def get_related_lot_obj(self, tender, complaint):
        cancellation = self.request.validated["cancellation"]
        if related_lot := cancellation.get("relatedLot"):
            for lot in tender.get("lots"):
                if lot["id"] == related_lot:
                    return lot


class CancellationComplaintState(CancellationComplaintStateMixin, TenderState):
    pass
