from datetime import timedelta

from openprocurement.api.constants_env import RELEASE_2020_04_19
from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import get_first_revision_date, raise_operation_error
from openprocurement.api.validation import OPERATIONS
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.utils import tender_created_after_2020_rules
from openprocurement.tender.core.procedure.validation import (
    validate_edrpou_confidentiality_doc,
    validate_field_change,
)
from openprocurement.tender.core.utils import calculate_tender_full_date


class CancellationStateMixing:
    # additionally to terminated
    cancellation_forbidden_statuses = {
        "active.auction",
        "active.qualification.stand-still",
        "draft",
    }

    # START Validations
    _before_release_reason_types = ["cancelled", "unsuccessful"]
    _after_release_reason_types = [
        "noDemand",
        "unFixable",
        "forceMajeure",
        "expensesCut",
    ]

    _before_release_statuses = ["pending", "active"]
    _after_release_statuses = ["draft", "pending", "unsuccessful", "active"]

    def validate_cancellation_post(self, data):
        request, tender = get_request(), get_tender()
        self.validate_cancellation_in_allowed_tender_status(request, tender, data)
        self.validate_cancellation_of_active_lot(request, tender, data)
        if tender_created_after_2020_rules():
            self.validate_pending_cancellation_present(request, tender, data)
            self.validate_cancellation_in_complaint_period(request, tender, data)
            self.validate_absence_of_pending_accepted_satisfied_complaints(request, tender, data)

        self.validate_possible_reason_types(request, tender, data)
        self.validate_cancellation_possible_statuses(request, tender, data)
        self.validate_docs(data)

    def validate_cancellation_patch(self, before, after):
        request, tender = get_request(), get_tender()
        self.validate_cancellation_in_allowed_tender_status(request, tender, before)
        self.validate_cancellation_of_active_lot(request, tender, before)
        self.validate_cancellation_status_draft_pending(request, tender, before)
        if tender_created_after_2020_rules():
            self.validate_pending_cancellation_present(request, tender, before)
            self.validate_cancellation_in_complaint_period(request, tender, before)
            # CS-12838
            self.validate_absence_of_pending_accepted_satisfied_complaints(request, tender, after)

        validate_field_change(
            field_name="reasonType",
            before_obj=before,
            after_obj=after,
            validator=self.validate_possible_reason_types,
            args=(request, tender, after),
        )
        self.validate_cancellation_possible_statuses(request, tender, after)
        self.validate_docs(after)

    def validate_cancellation_in_allowed_tender_status(self, request, tender, _):
        tender_status = tender.get("status")
        if tender_status in self.terminated_statuses or tender_status in self.cancellation_forbidden_statuses:
            raise_operation_error(
                request,
                f"Can't perform cancellation in current ({tender_status}) tender status",
            )

    @staticmethod
    def validate_cancellation_status_draft_pending(request, tender, cancellation):
        if cancellation["status"] not in ("draft", "pending"):
            raise_operation_error(
                request,
                f"Can't update cancellation in current ({cancellation['status']}) status",
            )

    def validate_possible_reason_types(self, request, tender, cancellation):
        reason_type = cancellation.get("reasonType")
        if tender_created_after_2020_rules():
            choices = self._after_release_reason_types
            if not reason_type:
                raise raise_operation_error(request, ["This field is required"], status=422, name="reasonType")
        else:
            choices = self._before_release_reason_types
            if not choices and reason_type:
                raise raise_operation_error(request, ["Rogue field"], status=422, name="reasonType")

            elif not choices and not reason_type:
                return

            elif not reason_type and choices:
                cancellation["reasonType"] = choices[0]
                return

        if reason_type not in choices:
            raise raise_operation_error(
                request,
                [f"Value must be one of {choices}"],
                status=422,
                name="reasonType",
            )

    def validate_cancellation_possible_statuses(self, request, tender, cancellation):
        choices = self._after_release_statuses if tender_created_after_2020_rules() else self._before_release_statuses
        status = cancellation.get("status")
        if status and status not in choices:
            raise raise_operation_error(request, [f"Value must be one of {choices}"], status=422, name="status")

    @staticmethod
    def validate_cancellation_of_active_lot(request, tender, cancellation):
        if any(
            lot.get("status") != "active"
            for lot in tender.get("lots", "")
            if lot["id"] == cancellation.get("relatedLot")
        ):
            raise_operation_error(request, "Can perform cancellation only in active lot status")

    @staticmethod
    def validate_pending_cancellation_present(request, tender, cancellation):
        related_lot = cancellation.get("relatedLot")  # can be None
        # cannot create two cancellation in pending
        # 1 for same lot
        # 2 for tender if there is a lot cancellation
        # 3 for lot if there is a tender cancellation
        if cancellation.get("status") != "pending" and any(
            c["status"] == "pending"
            and (c.get("relatedLot") == related_lot or c.get("relatedLot") is None or related_lot is None)
            for c in tender.get("cancellations", "")
        ):
            raise_operation_error(request, "Forbidden because of a pending cancellation")

    @staticmethod
    def validate_cancellation_in_complaint_period(request, tender, cancellation):
        operation = OPERATIONS.get(request.method)
        msg = f"Cancellation can't be {operation} when exists active complaint period"
        if tender["status"] == "active.pre-qualification.stand-still":
            raise_operation_error(request, msg)

        related_lot = cancellation.get("relatedLot")  # can be None
        for award in tender.get("awards", ""):
            if related_lot is None or related_lot == award.get("lotID"):
                complaint_period = award.get("complaintPeriod", {})
                complaint_end = complaint_period.get("endDate")
                if complaint_end and complaint_period.get("startDate") < get_request_now().isoformat() < complaint_end:
                    raise_operation_error(request, msg)

    @staticmethod
    def validate_absence_of_pending_accepted_satisfied_complaints(request, tender, cancellation):
        tender_creation_date = get_first_revision_date(tender, default=get_request_now())
        if tender_creation_date < RELEASE_2020_04_19:
            return

        cancellation_lot = cancellation.get("relatedLot")

        def validate_complaint(complaint, complaint_lot, item_name):
            """
            raise error if it's:
             - canceling tender that has a complaint (not cancellation_lot)
             - canceling tender that has a lot complaint (not cancellation_lot)
             - canceling lot that has a lot complaint (cancellation_lot == complaint_lot)
             - canceling lot if there is a non-lot complaint (not complaint_lot)
            AND complaint.status is in ("pending", "accepted", "satisfied")
            """
            if cancellation_lot == complaint_lot or None in (
                cancellation_lot,
                complaint_lot,
            ):  # same lot or both None
                status = complaint.get("status")
                if status in ("pending", "accepted", "satisfied"):
                    raise_operation_error(
                        request,
                        f"Can't perform operation for there is {item_name} complaint in {status} status",
                    )

        for c in tender.get("complaints", ""):
            validate_complaint(c, c.get("relatedLot"), "a tender")

        for qualification in tender.get("qualifications", ""):
            for c in qualification.get("complaints", ""):
                validate_complaint(c, qualification.get("lotID"), "a qualification")

        for award in tender.get("awards", ""):
            for c in award.get("complaints", ""):
                validate_complaint(c, award.get("lotID"), "an award")

    # END Validations

    def cancellation_on_post(self, data):
        if data["status"] == "active":
            self.cancel(data)
        self.always(get_tender())

    def cancellation_on_patch(self, before, after):
        if before["status"] != after["status"]:
            self.cancellation_status_up(before["status"], after["status"], after)
            self.always(get_tender())

    def validate_docs(self, data):
        for doc in data.get("documents", []):
            validate_edrpou_confidentiality_doc(doc)

    def cancellation_status_up(self, before, after, cancellation):
        request, tender = get_request(), get_tender()
        if before == "draft" and after == "pending":
            if not cancellation["reason"] or not cancellation.get("documents"):
                raise_operation_error(
                    request,
                    "Fields reason, cancellationOf and documents must be filled "
                    "for switch cancellation to pending status",
                    status=422,
                )
            self.validate_absence_of_pending_accepted_satisfied_complaints(request, tender, cancellation)
            cancellation_complain_duration = tender["config"]["cancellationComplainDuration"]
            if tender["config"]["hasCancellationComplaints"] is True and cancellation_complain_duration > 0:
                now = get_request_now()
                cancellation["complaintPeriod"] = {
                    "startDate": now.isoformat(),
                    "endDate": calculate_tender_full_date(
                        now,
                        timedelta(days=cancellation_complain_duration),
                        tender=tender,
                    ).isoformat(),
                }
            else:
                self.set_object_status(cancellation, "active")
                self.cancel(cancellation)

        # TODO: deprecated logic for belowThreshold, cfaselection, PQ and limited procedures
        elif (
            before in ("draft", "pending")
            and after == "active"
            and (
                tender["config"]["hasCancellationComplaints"] is False
                or self.use_deprecated_activation(cancellation, tender)
            )
        ):
            if tender_created_after_2020_rules() and (not cancellation["reason"] or not cancellation.get("documents")):
                raise_operation_error(
                    request,
                    "Fields reason, cancellationOf and documents must be filled "
                    "for switch cancellation to active status",
                    status=422,
                )
            self.cancel(cancellation)
        elif before == "draft" and after == "unsuccessful":
            pass
        elif (
            before == "pending"
            and after == "unsuccessful"
            and any(i["status"] == "satisfied" for i in cancellation.get("complaints", ""))
        ):
            pass
        elif after == "active" and not tender_created_after_2020_rules():
            self.cancel(cancellation)
        else:
            raise_operation_error(request, f"Can't switch cancellation status from {before} to {after}")

    @staticmethod
    def use_deprecated_activation(cancellation, tender):
        return False


class CancellationState(CancellationStateMixing, TenderState):
    pass
