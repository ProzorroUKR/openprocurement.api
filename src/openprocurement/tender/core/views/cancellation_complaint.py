# -*- coding: utf-8 -*-
from iso8601 import parse_date
from datetime import timedelta

from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.utils import (
    get_now,
    context_unpack,
    json_view,
    set_ownership,
    APIResource,
    raise_operation_error,
    get_first_revision_date,
)
from openprocurement.tender.core.validation import (
    validate_complaint_data,
    validate_patch_complaint_data,
    validate_cancellation_complaint,
    validate_cancellation_complaint_add_only_in_pending,
    validate_cancellation_complaint_resolved,
    validate_update_cancellation_complaint_not_in_allowed_complaint_status,
)
from openprocurement.tender.belowthreshold.utils import check_tender_status
from openprocurement.tender.core.views.complaint import ComplaintAdminPatchMixin, ComplaintBotPatchMixin
from openprocurement.tender.core.utils import (
    save_tender, apply_patch, calculate_total_complaints, calculate_tender_business_date
)


class TenderCancellationComplaintResource(ComplaintBotPatchMixin, ComplaintAdminPatchMixin, APIResource):
    patch_check_tender_excluded_statuses = (
        "draft", "pending", "accepted", "satisfied", "stopping",
    )

    @json_view(
        content_type="application/json",
        permission="create_cancellation_complaint",
        validators=(
                validate_cancellation_complaint,
                validate_complaint_data,
                validate_cancellation_complaint_add_only_in_pending,
                validate_cancellation_complaint_resolved,
        ),
    )
    def collection_post(self):
        """Post a complaint for cancellation
        """
        tender = self.request.validated["tender"]
        complaint = self.request.validated["complaint"]

        complaint.date = get_now()

        complaint.complaintID = "{}.{}{}".format(
            tender.tenderID,
            self.server_id,
            calculate_total_complaints(tender) + 1
        )
        access = set_ownership(complaint, self.request)
        self.context.complaints.append(complaint)
        if save_tender(self.request):
            self.LOGGER.info(
                "Created tender cancellation complaint {}".format(complaint.id),
                extra=context_unpack(
                    self.request, {"MESSAGE_ID": "tender_cancellation_complaint_create"}, {"complaint_id": complaint.id}
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tender Cancellation Complaints".format(tender.procurementMethodType),
                tender_id=tender.id,
                cancellation_id=self.request.validated["cancellation_id"],
                complaint_id=complaint["id"],
            )
            return {"data": complaint.serialize("view"), "access": access}

    @json_view(permission="view_tender", validators=(validate_cancellation_complaint,))
    def collection_get(self):
        """List complaints for cancellations
        """
        return {"data": [i.serialize("view") for i in self.context.complaints]}

    @json_view(permission="view_tender", validators=(validate_cancellation_complaint,))
    def get(self):
        """Retrieving the complaint for cancellation
        """
        return {"data": self.context.serialize("view")}

    @json_view(
        content_type="application/json",
        permission="edit_complaint",
        validators=(
                validate_patch_complaint_data,
                validate_cancellation_complaint_resolved,
                validate_update_cancellation_complaint_not_in_allowed_complaint_status,
        ),
    )
    def patch(self):
        role_method_name = "patch_as_{role}".format(role=self.request.authenticated_role.lower())
        try:
            role_method = getattr(self, role_method_name)
        except AttributeError:
            raise_operation_error(self.request, "Can't update complaint as {}".format(self.request.authenticated_role))
        else:
            role_method(self.request.validated["data"])

        if self.context.tendererAction and not self.context.tendererActionDate:
            self.context.tendererActionDate = get_now()
            self.context.status = "resolved"
            self.recalculate_tender_periods()

        if (
                self.context.status not in self.patch_check_tender_excluded_statuses
                and self.request.validated["tender"].status in ("active.qualification", "active.awarded")
        ):
            check_tender_status(self.request)

        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender cancellation complaint {}".format(self.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_cancellation_complaint_patch"}),
            )
            return {"data": self.context.serialize("view")}

    def patch_as_complaint_owner(self, data):
        status = self.context.status
        new_status = data.get("status", status)
        if (
            status == "draft" and new_status == "cancelled"
            or status in ["pending", "accepted"] and new_status == "stopping"
        ):
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateCanceled = get_now()

        elif status == "draft":
            self.patch_draft_as_complaint_owner(data)

        else:
            raise_operation_error(
                self.request,
                "Can't update complaint from {} to {} status".format(status, new_status)
            )

    def patch_draft_as_complaint_owner(self, data):
        tender = self.request.validated["tender"]
        context = self.context
        status = context.status
        new_status = data.get("status", self.context.status)
        if new_status == self.context.status:
            apply_patch(self.request, save=False, src=context.serialize())
        elif status == "draft" and new_status == "mistaken":
            context.rejectReason = "cancelledByComplainant"
            apply_patch(self.request, save=False, src=context.serialize())
        elif new_status == "pending" and get_first_revision_date(tender, get_now()) < RELEASE_2020_04_19:
            apply_patch(self.request, save=False, src=context.serialize())
            context.dateSubmitted = get_now()
        else:
            raise_operation_error(self.request, "Can't update draft complaint into {} status".format(new_status))

    def patch_as_tender_owner(self, data):
        context = self.context
        status = context.status
        new_status = data.get("status", status)

        if status in ["pending", "accepted"] or new_status == status and status in ["satisfied"]:
            apply_patch(self.request, save=False, src=context.serialize())
        elif (
            status == "satisfied"
            and data.get("tendererAction", context.tendererAction)
            and new_status == "resolved"
        ):
            apply_patch(self.request, save=False, src=context.serialize())
        else:
            raise_operation_error(self.request,
                                  "Can't update complaint from {} to {} status".format(status, new_status))

    def patch_as_abovethresholdreviewers(self, data):
        context = self.context
        status = context.status
        new_status = data.get("status", status)

        if new_status == status and status in ["pending", "accepted", "stopping"]:
            apply_patch(self.request, save=False, src=context.serialize())

        elif status in ["pending", "stopping"] and new_status == "invalid":
            apply_patch(self.request, save=False, src=context.serialize())
            context.dateDecision = get_now()
            context.acceptance = False

        elif status == "pending" and new_status == "accepted":
            apply_patch(self.request, save=False, src=context.serialize())
            context.dateAccepted = get_now()
            context.acceptance = True

        elif status in ["accepted", "stopping"] and new_status in ["declined", "satisfied"]:
            apply_patch(self.request, save=False, src=context.serialize())
            context.dateDecision = get_now()
            if new_status == "satisfied":
                self.on_satisfy_complaint_by_reviewer()
        elif status == "accepted" and new_status == "stopped":
            apply_patch(self.request, save=False, src=context.serialize())
            context.dateDecision = get_now()
            context.dateCanceled = context.dateCanceled or get_now()
        else:
            raise_operation_error(self.request,
                                  "Can't update complaint from {} to {} status".format(status, new_status))

    def on_satisfy_complaint_by_reviewer(self):
        pass

    def recalculate_tender_periods(self):
        tender = self.request.validated["tender"]
        cancellation = self.request.validated["cancellation"]
        tenderer_action_date = self.context.tendererActionDate

        enquiry_period = tender.enquiryPeriod
        tender_period = tender.tenderPeriod
        auction_period = tender.auctionPeriod

        date = cancellation.complaintPeriod.startDate

        delta = (tenderer_action_date - date).days
        delta_plus = 1 if (tenderer_action_date - date).seconds > 3599 else 0

        delta += delta_plus

        delta = timedelta(days=1 if not delta else delta)

        if tender.status == "active.tendering" and tender.enquiryPeriod:

            if enquiry_period.startDate < date <= tender_period.endDate:

                if enquiry_period.endDate:
                    enquiry_period.endDate = calculate_tender_business_date(
                        enquiry_period.endDate, delta, tender)
                if enquiry_period.clarificationsUntil:
                    enquiry_period.clarificationsUntil = calculate_tender_business_date(
                        enquiry_period.clarificationsUntil, delta, tender)

                if tender_period.endDate:
                    tender_period.endDate = calculate_tender_business_date(
                        tender_period.endDate, delta, tender)

                if auction_period.shouldStartAfter:
                    auction_period.shouldStartAfter = calculate_tender_business_date(
                        parse_date(auction_period.shouldStartAfter), delta, tender).isoformat()

                if auction_period.startDate:
                    auction_period.startDate = calculate_tender_business_date(
                        auction_period.startDate, delta, tender)

            elif auction_period and tender_period.endDate and auction_period.shouldStartAfter\
                    and tender_period.endDate < date <= parse_date(auction_period.shouldStartAfter):

                auction_period.shouldStartAfter = calculate_tender_business_date(
                    auction_period.shouldStartAfter, delta, tender)
                auction_period.startDate = calculate_tender_business_date(
                    auction_period.startDate, delta, tender)
