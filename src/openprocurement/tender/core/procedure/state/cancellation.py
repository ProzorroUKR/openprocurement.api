from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS
from openprocurement.tender.core.utils import calculate_complaint_business_date
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.context import get_tender, get_request
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.utils import since_2020_rules
from datetime import timedelta


class CancellationStateMixing:
    # from BaseState
    set_object_status: callable

    # from base tender state
    always: callable
    terminated_statuses: tuple
    count_lot_bids_number: callable
    min_bids_number: callable

    # from awarding mixing
    add_next_award: callable

    # additionally to terminated
    cancellation_forbidden_statuses = {"active.auction", "active.qualification.stand-still", "draft"}

    # START Validations
    _before_release_reason_types = ["cancelled", "unsuccessful"]
    _after_release_reason_types = ["noDemand", "unFixable", "forceMajeure", "expensesCut"]

    _before_release_statuses = ["pending", "active"]
    _after_release_statuses = ["draft", "pending", "unsuccessful", "active"]

    def validate_cancellation_post(self, data):
        request, tender = get_request(), get_tender()
        self.validate_cancellation_in_allowed_tender_status(request, tender, data)
        self.validate_cancellation_of_active_lot(request, tender, data)
        if since_2020_rules():
            self.validate_pending_cancellation_present(request, tender, data)
            self.validate_cancellation_in_complaint_period(request, tender, data)
            self.validate_absence_of_pending_accepted_satisfied_complaints(request, tender, data)

        self.validate_possible_reason_types(request, tender, data)
        self.validate_cancellation_possible_statuses(request, tender, data)

    def validate_cancellation_patch(self, before, after):
        request, tender = get_request(), get_tender()
        self.validate_cancellation_in_allowed_tender_status(request, tender, before)
        self.validate_cancellation_of_active_lot(request, tender, before)
        self.validate_cancellation_status_draft_pending(request, tender, before)
        if since_2020_rules():
            self.validate_pending_cancellation_present(request, tender, before)
            self.validate_cancellation_in_complaint_period(request, tender, before)
            # CS-12838
            self.validate_absence_of_pending_accepted_satisfied_complaints(request, tender, after)

        self.validate_possible_reason_types(request, tender, after)
        self.validate_cancellation_possible_statuses(request, tender, after)

    def validate_cancellation_in_allowed_tender_status(self, request, tender, _):
        tender_status = tender.get("status")
        if tender_status in self.terminated_statuses or tender_status in self.cancellation_forbidden_statuses:
            raise_operation_error(request, f"Can't perform cancellation in current ({tender_status}) tender status")

    @staticmethod
    def validate_cancellation_status_draft_pending(request, tender, cancellation):
        if cancellation['status'] not in ("draft", "pending"):
            raise_operation_error(
                request,
                f"Can't update cancellation in current ({cancellation['status']}) status"
            )

    def validate_possible_reason_types(self, request, tender, cancellation):
        reason_type = cancellation.get("reasonType")
        if since_2020_rules():
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
            raise raise_operation_error(request, [f"Value must be one of {choices}"], status=422, name="reasonType")

    def validate_cancellation_possible_statuses(self, request, tender, cancellation):
        choices = (
            self._after_release_statuses
            if since_2020_rules()
            else self._before_release_statuses
        )
        status = cancellation.get("status")
        if status and status not in choices:
            raise raise_operation_error(request, [f"Value must be one of {choices}"], status=422, name="status")

    @staticmethod
    def validate_cancellation_of_active_lot(request, tender, cancellation):
        if any(lot.get("status") != "active"
               for lot in tender.get("lots", "")
               if lot["id"] == cancellation.get("relatedLot")):
            raise_operation_error(request, "Can perform cancellation only in active lot status")

    @staticmethod
    def validate_pending_cancellation_present(request, tender, cancellation):
        related_lot = cancellation.get("relatedLot")  # can be None
        # cannot create two cancellation in pending
        # 1 for same lot
        # 2 for tender if there is a lot cancellation
        # 3 for lot if there is a tender cancellation
        if (
            cancellation.get("status") != "pending"
            and any(
                c["status"] == "pending"
                and (
                    c.get("relatedLot") == related_lot
                    or c.get("relatedLot") is None
                    or related_lot is None
                )
                for c in tender.get("cancellations", "")
            )
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
                if complaint_end and complaint_period.get("startDate") < get_now().isoformat() < complaint_end:
                        raise_operation_error(request, msg)

    @staticmethod
    def validate_absence_of_pending_accepted_satisfied_complaints(request, tender, cancellation):
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
            if (
                cancellation_lot == complaint_lot  # same lot or both None
                or None in (cancellation_lot, complaint_lot)
            ):
                status = complaint.get("status")
                if status in ("pending", "accepted", "satisfied"):
                    raise_operation_error(
                        request,
                        f"Can't perform operation for there is {item_name} complaint in {status} status"
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
            self.cancel_tender_lot(data)
        self.always(get_tender())

    def cancellation_on_patch(self, before, after):
        if before["status"] != after["status"]:
            self.cancellation_status_up(before["status"], after["status"], after)
            self.always(get_tender())

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
            now = get_now()
            cancellation["complaintPeriod"] = {
                "startDate": now.isoformat(),
                "endDate": calculate_complaint_business_date(now, timedelta(days=10), tender).isoformat()
            }
        elif before == "draft" and after == "unsuccessful":
            pass
        elif before == "pending" and after == "unsuccessful" \
                and any(i["status"] == "satisfied" for i in cancellation.get("complaints", "")):
            pass
        elif after == "active" and not since_2020_rules():
            self.cancel_tender_lot(cancellation)
        else:
            raise_operation_error(request, f"Can't switch cancellation status from {before} to {after}")

    # START Cancelling
    def cancel_tender_lot(self, cancellation):
        request, tender = get_request(), get_tender()
        if since_2020_rules():  # TODO: does it make sense to do validation here?
            self.validate_absence_of_pending_accepted_satisfied_complaints(request, tender, cancellation)
        if cancellation["cancellationOf"] == "lot":
            self.cancel_lot(tender, cancellation)
        else:
            self.cancel_tender(tender)

    def cancel_tender(self, tender):
        if tender["status"] in ("active.tendering", "active.auction"):
            tender.pop("bids", None)
        self.set_object_status(tender, "cancelled")

    def cancel_lot(self, tender, cancellation):
        self._cancel_lot(tender, cancellation["relatedLot"])
        self._lot_update_check_tender_status(tender)

        if tender["status"] == "active.auction" and all(
            "endDate" in i.get("auctionPeriod", "")
            for i in tender.get("lots", "")
            if self.count_lot_bids_number(tender, cancellation["relatedLot"]) > self.min_bids_number
            and i["status"] == "active"
        ):
            self.add_next_award()

    def _lot_update_check_tender_status(self, tender):
        lot_statuses = {lot["status"] for lot in tender.get("lots", "")}
        if lot_statuses == {"cancelled"}:
            self.cancel_tender(tender)
        elif not lot_statuses.difference({"unsuccessful", "cancelled"}):
            self.set_object_status(tender, "unsuccessful")
        elif not lot_statuses.difference({"complete", "unsuccessful", "cancelled"}):
            self.set_object_status(tender, "complete")

    def _cancel_lot(self, tender, lot_id):
        for lot in tender.get("lots", ""):
            if lot["id"] == lot_id:
                self.set_object_status(lot, "cancelled")
    # END Cancelling


class CancellationState(CancellationStateMixing, TenderState):
    pass
