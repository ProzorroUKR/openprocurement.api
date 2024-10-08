from logging import getLogger

from openprocurement.api.context import get_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS
from openprocurement.tender.core.procedure.models.complaint import (
    DraftPatchQualificationComplaint,
)
from openprocurement.tender.core.procedure.state.complaint import ComplaintStateMixin
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.utils import dt_from_iso

LOGGER = getLogger(__name__)


class QualificationComplaintStateMixin(ComplaintStateMixin):
    create_allowed_tender_statuses = ("active.pre-qualification.stand-still",)
    update_allowed_tender_statuses = (
        "active.pre-qualification",
        "active.pre-qualification.stand-still",
    )
    draft_patch_model = DraftPatchQualificationComplaint
    complaints_configuration = "hasQualificationComplaints"

    def complaint_on_post(self, complaint):
        request = self.request
        if lot_id := request.validated["qualification"].get("lotID"):
            complaint["relatedLot"] = lot_id
        super().complaint_on_post(complaint)

    def validate_tender_in_complaint_period(self, tender):
        if period := self.request.validated["qualification"].get("complaintPeriod"):
            period_start = period.get("startDate")
            period_end = period.get("endDate")
        else:
            period = tender.get("qualificationPeriod")
            period_start = period.get("reportingDatePublication")
            period_end = period.get("endDate")
        now = get_now()
        if not period_start or not period_end or now < dt_from_iso(period_start) or now > dt_from_iso(period_end):
            raise_operation_error(self.request, "Can add complaint only in complaintPeriod")

    def validate_lot_status(self):
        tender = get_tender()
        qualification = self.request.validated["qualification"]
        lot_id = qualification.get("lotID")
        if lot_id and any(lot.get("status") != "active" for lot in tender.get("lots", []) if lot["id"] == lot_id):
            operation = OPERATIONS.get(self.request.method)
            raise_operation_error(self.request, f"Can {operation} complaint only in active lot status")

    def get_related_lot_obj(self, tender, complaint):
        qualification = self.request.validated["qualification"]
        if related_lot := qualification.get("lotID"):
            for lot in tender.get("lots"):
                if lot["id"] == related_lot:
                    return lot

    def reviewers_satisfied_handler(self, complaint):
        super().reviewers_satisfied_handler(complaint)
        tender = get_tender()
        self.get_change_tender_status_handler("active.pre-qualification")(tender)


class QualificationComplaintState(QualificationComplaintStateMixin, TenderState):
    pass
