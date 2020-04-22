# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
    raise_operation_error,
    get_first_revision_date,
    get_now,
)
from openprocurement.api.constants import RELEASE_2020_04_19

from openprocurement.tender.core.utils import apply_patch, optendersresource

from openprocurement.tender.core.validation import (
    validate_add_complaint_not_in_complaint_period,
    validate_update_complaint_not_in_allowed_complaint_status,
    validate_add_complaint_with_tender_cancellation_in_pending,
    validate_add_complaint_with_lot_cancellation_in_pending,
)

from openprocurement.tender.limited.validation import (
    validate_complaint_data,
    validate_patch_complaint_data,
    validate_award_complaint_operation_not_in_active,
)

from openprocurement.tender.core.views.award_complaint import BaseTenderAwardComplaintResource


@optendersresource(
    name="negotiation:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="negotiation",
    description="Tender negotiation award complaints",
)
class TenderNegotiationAwardComplaintResource(BaseTenderAwardComplaintResource):

    patch_check_tender_excluded_statuses = "__all__"

    def complaints_len(self, tender):
        return sum([len(i.complaints) for i in tender.awards])

    def pre_create(self):
        tender = self.request.validated["tender"]
        old_rules = get_first_revision_date(tender) < RELEASE_2020_04_19

        complaint = self.request.validated["complaint"]
        complaint.date = get_now()
        complaint.type = "complaint"
        if old_rules and complaint.status == "pending":
            complaint.dateSubmitted = get_now()
        else:
            complaint.status = "draft"

        return complaint

    @json_view(
        content_type="application/json",
        permission="create_award_complaint",
        validators=(
            validate_complaint_data,
            validate_award_complaint_operation_not_in_active,
            validate_add_complaint_not_in_complaint_period,
            validate_add_complaint_with_tender_cancellation_in_pending,
            validate_add_complaint_with_lot_cancellation_in_pending("award"),
        ),
    )
    def collection_post(self):
        """Post a complaint for award
        """
        return super(TenderNegotiationAwardComplaintResource, self).collection_post()

    @json_view(
        content_type="application/json",
        permission="edit_complaint",
        validators=(
            validate_patch_complaint_data,
            validate_award_complaint_operation_not_in_active,
            validate_update_complaint_not_in_allowed_complaint_status,
        ),
    )
    def patch(self):
        return super(TenderNegotiationAwardComplaintResource, self).patch()

    def patch_as_complaint_owner(self, data):
        complaint_period = self.request.validated["award"].complaintPeriod
        is_complaint_period = (
            complaint_period.startDate <= get_now() <= complaint_period.endDate
            if complaint_period.endDate
            else complaint_period.startDate <= get_now()
        )
        status = self.context.status
        new_status = data.get("status", status)

        tender = self.request.validated["tender"]
        new_rules = get_first_revision_date(tender) > RELEASE_2020_04_19

        if status in ["draft", "claim", "answered"] and new_status == "cancelled":
            # claim ? There is no way to post claim, so this must be a backward-compatibility option
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateCanceled = get_now()
        elif status in ["pending", "accepted"] and new_status == "stopping":
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateCanceled = get_now()
        elif status == "draft":
            if not is_complaint_period:
                raise_operation_error(self.request, "Can't update draft complaint not in complaintPeriod")
            if new_status == status:
                apply_patch(self.request, save=False, src=self.context.serialize())
            elif (
                new_rules
                and self.context.type == "complaint"
                and new_status == "mistaken"
            ):
                self.context.rejectReason = "cancelledByComplainant"
                apply_patch(self.request, save=False, src=self.context.serialize())
            elif new_status == "pending" and not new_rules:
                apply_patch(self.request, save=False, src=self.context.serialize())
                self.context.type = "complaint"
                self.context.dateSubmitted = get_now()
            else:
                raise_operation_error(self.request, "Can't update draft complaint to {} status".format(new_status))
        else:
            raise_operation_error(self.request, "Can't update complaint from {} to {}".format(status, new_status))

    def patch_as_tender_owner(self, data):
        status = self.context.status
        new_status = data.get("status", status)
        if status in ["pending", "accepted"]:
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif status == "satisfied" and new_status == status:
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif status == "satisfied" and new_status == "resolved":
            if not data.get("tendererAction", self.context.tendererAction):
                raise_operation_error(self.request, "Can't update complaint: tendererAction required")
            apply_patch(self.request, save=False, src=self.context.serialize())
        else:
            raise_operation_error(self.request, "Can't update complaint from {} to {}".format(status, new_status))

    def patch_as_abovethresholdreviewers(self, data):
        status = self.context.status
        new_status = data.get("status", status)

        tender = self.request.validated["tender"]
        old_rules = get_first_revision_date(tender) < RELEASE_2020_04_19

        if status in ["pending", "accepted", "stopping"] and new_status == status:
            apply_patch(self.request, save=False, src=self.context.serialize())

        elif (
            status in ["pending", "stopping"] 
            and (
                (old_rules and new_status in ["invalid", "mistaken"])
                or (new_status == "invalid")
            )
        ):
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateDecision = get_now()
            self.context.acceptance = False

        elif status == "pending" and new_status == "accepted":
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateAccepted = get_now()
            self.context.acceptance = True

        elif status in ["accepted", "stopping"] and new_status in ["declined", "satisfied"]:
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateDecision = get_now()

        elif (
            (old_rules and status in ["pending", "accepted", "stopping"])
            or (not old_rules and status in ["accepted", "stopping"])
            and new_status == "stopped"
        ):
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateDecision = get_now()
            self.context.dateCanceled = self.context.dateCanceled or get_now()

        else:
            raise_operation_error(self.request, "Can't update complaint from {} to {}".format(status, new_status))


@optendersresource(
    name="negotiation.quick:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="negotiation.quick",
    description="Tender negotiation.quick award complaints",
)
class TenderNegotiationQuickAwardComplaintResource(TenderNegotiationAwardComplaintResource):
    """ Tender Negotiation Quick Award Complaint Resource """
