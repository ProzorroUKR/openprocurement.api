from openprocurement.tender.core.procedure.utils import tender_created_after_2020_rules, dt_from_iso
from openprocurement.tender.core.procedure.state.complaint import ComplaintState
from openprocurement.tender.core.procedure.context import get_award, get_tender
from openprocurement.api.context import get_now
from openprocurement.api.validation import OPERATIONS
from logging import getLogger
from openprocurement.api.utils import raise_operation_error
from datetime import timedelta


LOGGER = getLogger(__name__)


class AwardComplaintState(ComplaintState):
    tender_complaint_submit_time = timedelta(days=4)
    create_allowed_tender_statuses = ("active.qualification", "active.awarded")
    update_allowed_tender_statuses = ("active.qualification", "active.awarded")

    def validate_complaint_on_post(self, complaint):
        super().validate_complaint_on_post(complaint)
        self.validate_submission_allowed()

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
            lot.get("status") != "active"
            for lot in tender.get("lots", [])
            if lot["id"] == award.get("lotID")
        ):
            operation = OPERATIONS.get(self.request.method)
            raise_operation_error(self.request, f"Can {operation} complaint only in active lot status")

    def get_related_lot_obj(self, tender, complaint):
        award = get_award()
        if related_lot := award.get("lotID"):
            for lot in tender.get("lots"):
                if lot["id"] == related_lot:
                    return lot
