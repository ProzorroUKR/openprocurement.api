from datetime import timedelta
from logging import getLogger

from openprocurement.api.context import get_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS
from openprocurement.tender.core.procedure.context import get_award
from openprocurement.tender.core.procedure.models.complaint import (
    DraftPatchAwardComplaint,
)
from openprocurement.tender.core.procedure.state.complaint import ComplaintStateMixin
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.utils import (
    dt_from_iso,
    tender_created_after_2020_rules,
)

LOGGER = getLogger(__name__)


class AwardComplaintStateMixin(ComplaintStateMixin):
    tender_complaint_submit_time = timedelta(days=4)
    create_allowed_tender_statuses = ("active.qualification", "active.awarded")
    update_allowed_tender_statuses = ("active.qualification", "active.awarded")
    draft_patch_model = DraftPatchAwardComplaint
    complaints_configuration = "hasAwardComplaints"

    def complaint_on_post(self, complaint):
        request = self.request
        if lot_id := request.validated["award"].get("lotID"):
            complaint["relatedLot"] = lot_id
        super().complaint_on_post(complaint)

    def validate_complaint_on_post(self, complaint):
        super().validate_complaint_on_post(complaint)
        self.validate_submission_allowed()
        self.validate_complaint_bidder_for_unsuccessful_award(complaint)

    def validate_submission_allowed(self):
        request = self.request
        tender = request.validated["tender"]
        context_award = request.validated["award"]

        if tender_created_after_2020_rules():
            if context_award.get("status") not in ("active", "unsuccessful"):
                raise_operation_error(
                    request,
                    "Complaint submission is allowed only after award activation or unsuccessful award.",
                )
        else:
            if not any(
                award.get("status") == "active"
                for award in tender.get("awards", [])
                if award.get("lotID") == context_award.get("lotID")
            ):
                raise_operation_error(request, "Complaint submission is allowed only after award activation.")

    def validate_tender_in_complaint_period(self, tender):
        award = get_award()
        period = award.get("complaintPeriod")
        if award.get("status") in ("active", "unsuccessful") and period:
            if dt_from_iso(period.get("startDate")) <= get_now() < dt_from_iso(period.get("endDate")):
                return
        raise_operation_error(self.request, "Can add complaint only in complaintPeriod")

    def validate_lot_status(self):
        tender = get_tender()
        award = get_award()
        lot_id = award.get("lotID")
        if lot_id and any(
            lot.get("status") != "active" for lot in tender.get("lots", []) if lot["id"] == award.get("lotID")
        ):
            operation = OPERATIONS.get(self.request.method)
            raise_operation_error(self.request, f"Can {operation} complaint only in active lot status")

    def get_related_lot_obj(self, tender, complaint):
        award = get_award()
        if related_lot := award.get("lotID"):
            for lot in tender.get("lots"):
                if lot["id"] == related_lot:
                    return lot

    def validate_complaint_bidder_for_unsuccessful_award(self, complaint):
        award = get_award()
        if award.get("status") == "unsuccessful" and award.get("bid_id") != complaint.get("bid_id"):
            raise_operation_error(
                self.request,
                "Can add complaint only on unsuccessful award of your bid",
                status=422,
                name="bid_id",
            )


class AwardComplaintState(AwardComplaintStateMixin, TenderState):
    pass
