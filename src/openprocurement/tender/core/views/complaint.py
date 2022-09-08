# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    context_unpack, 
    json_view, 
    set_ownership, 
    raise_operation_error,
    get_first_revision_date,
    get_now,
)
from openprocurement.api.views.base import BaseResource
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.core.validation import (
    validate_complaint_data,
    validate_patch_complaint_data,
    validate_update_complaint_not_in_allowed_complaint_status,
    validate_update_complaint_not_in_allowed_claim_status,
    validate_complaint_operation_not_in_active_tendering,
    validate_submit_complaint_time,
    validate_complaint_update_with_cancellation_lot_pending,
    validate_add_complaint_with_tender_cancellation_in_pending,
    validate_add_complaint_with_lot_cancellation_in_pending,
    validate_operation_with_lot_cancellation_in_pending,
)
from openprocurement.tender.belowthreshold.utils import check_tender_status
from openprocurement.tender.core.utils import save_tender, apply_patch, calculate_total_complaints


class ComplaintAdminPatchMixin(object):
    def patch_as_administrator(self, *_):
        apply_patch(self.request, save=False, src=self.context.serialize())


class ComplaintBotPatchMixin(object):
    def patch_as_bots(self, data):
        request = self.request
        context = self.context

        status = context.status
        new_status = data.get("status", status)

        tender = request.validated["tender"]
        new_rules = get_first_revision_date(tender, default=get_now()) > RELEASE_2020_04_19

        if new_rules and status == "draft" and new_status in ["pending", "mistaken"]:
            if new_status == "mistaken":
                context.rejectReason = "incorrectPayment"
            elif new_status == "pending":
                context.dateSubmitted = get_now()
            apply_patch(request, save=False, src=context.serialize())
        else:
            raise_operation_error(
                request,
                "Can't update complaint from {} to {} status".format(status, new_status)
            )


class BaseComplaintGetResource(BaseResource):
    @json_view(permission="view_tender")
    def get(self):
        """Retrieving the complaint
        """
        return {"data": self.context.serialize("view")}

    @json_view(permission="view_tender")
    def collection_get(self):
        """List complaints
        """
        return {"data": [i.serialize("view") for i in self.context.complaints]}


class BaseTenderComplaintResource(ComplaintBotPatchMixin, ComplaintAdminPatchMixin, BaseResource):
    patch_check_tender_excluded_statuses = (
        "draft", "pending", "accepted", "satisfied", "stopping",
    )

    patch_check_tender_statuses = ("active.qualification", "active.awarded")

    def pre_create(self):
        tender = self.request.validated["tender"]
        old_rules = get_first_revision_date(tender) < RELEASE_2020_04_19

        complaint = self.request.validated["complaint"]
        complaint.date = get_now()

        if old_rules and complaint.status == "pending":
            # TODO why don`t we use self.validate_submit_complaint_time?
            validate_submit_complaint_time(self.request)
            complaint.dateSubmitted = get_now()
        else:
            validate_submit_complaint_time(self.request)
            complaint.status = "draft"
        return complaint

    @json_view(
        content_type="application/json",
        validators=(
            validate_complaint_data,
            validate_complaint_operation_not_in_active_tendering,
            validate_add_complaint_with_tender_cancellation_in_pending,
            validate_add_complaint_with_lot_cancellation_in_pending("complaint"),
        ),
        permission="create_complaint",
    )
    def collection_post(self):
        """Post a complaint for award
        """
        tender = self.request.validated["tender"]

        complaint = self.pre_create()

        complaint.complaintID = "{}.{}{}".format(
            tender.tenderID,
            self.server_id,
            calculate_total_complaints(tender) + 1
        )
        access = set_ownership(complaint, self.request)
        self.context.complaints.append(complaint)
        if save_tender(self.request):
            self.LOGGER.info(
                "Created tender award complaint {}".format(complaint.id),
                extra=context_unpack(
                    self.request, {"MESSAGE_ID": "tender_complaint_create"}, {"complaint_id": complaint.id}
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tender Complaints".format(tender.procurementMethodType),
                tender_id=tender.id,
                complaint_id=complaint.id,
            )
            return {"data": complaint.serialize(tender.status), "access": access}

    @json_view(
        content_type="application/json",
        permission="edit_complaint",
        validators=(
            validate_patch_complaint_data,
            validate_complaint_update_with_cancellation_lot_pending,
            validate_complaint_operation_not_in_active_tendering,
            validate_update_complaint_not_in_allowed_complaint_status,
            validate_operation_with_lot_cancellation_in_pending("complaint"),
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
        if (
            self.patch_check_tender_excluded_statuses != "__all__"
            and self.context.status not in self.patch_check_tender_excluded_statuses
            and self.request.validated["tender"].status in self.patch_check_tender_statuses
        ):
            check_tender_status(self.request)

        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender award complaint {}".format(self.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_award_complaint_patch"}),
            )
            return {"data": self.context.serialize("view")}

    def patch_as_complaint_owner(self, data):
        context = self.context
        status = self.context.status
        new_status = data.get("status", status)

        tender = self.request.validated["tender"]
        apply_rules_2020_04_19 = get_first_revision_date(tender) > RELEASE_2020_04_19

        if (
            new_status == "cancelled"
            and status == "draft"
            and not apply_rules_2020_04_19
        ):
            apply_patch(self.request, save=False, src=context.serialize())
            context.dateCanceled = get_now()
        
        elif (
            apply_rules_2020_04_19
            and status == "draft"
            and new_status == "mistaken"
        ):
            context.rejectReason = "cancelledByComplainant"
            apply_patch(self.request, save=False, src=context.serialize())
        
        elif (
            status in ["pending", "accepted"]
            and new_status == "stopping"
            and not apply_rules_2020_04_19
        ):
            apply_patch(self.request, save=False, src=context.serialize())
            context.dateCanceled = get_now()
        elif (
            tender.status == "active.tendering"
            and status == "draft"
            and new_status == status
        ):
            apply_patch(self.request, save=False, src=context.serialize())
        elif (
            tender.status == "active.tendering"
            and status in ["draft"]
            and new_status == "pending"
            and not apply_rules_2020_04_19
        ):
            validate_submit_complaint_time(self.request)
            apply_patch(self.request, save=False, src=context.serialize())
            context.dateSubmitted = get_now()
        
        else:
            raise_operation_error(
                self.request,
                "Can't update complaint from {} to {} status".format(status, new_status)
            )
    
    def patch_as_tender_owner(self, data):
        context = self.context
        status = context.status
        new_status = data.get("status", status)

        if status == "satisfied" and new_status == status:
            apply_patch(self.request, save=False, src=context.serialize())
        
        elif status in ["pending", "accepted"]:
            apply_patch(self.request, save=False, src=context.serialize())
        elif (
            status == "satisfied"
            and data.get("tendererAction", context.tendererAction)
            and new_status == "resolved"
        ):
            apply_patch(self.request, save=False, src=context.serialize())
        else:
            raise_operation_error(
                self.request,
                "Can't update complaint from {} to {} status".format(status, new_status)
            )
            
    def patch_as_abovethresholdreviewers(self, data):
        context = self.context
        status = context.status
        new_status = data.get("status", status)

        tender = self.request.validated["tender"]
        old_rules = get_first_revision_date(tender) < RELEASE_2020_04_19

        if (
            status in ["pending", "accepted", "stopping"]
            and new_status == status
        ):
            apply_patch(self.request, save=False, src=context.serialize())
        elif (
            status in ["pending", "stopping"]
            and (
                (old_rules and new_status in ["invalid", "mistaken"]) 
                or (new_status == "invalid")
            )
        ):
            apply_patch(self.request, save=False, src=context.serialize())
            context.dateDecision = get_now()
            context.acceptance = False
        elif status == "pending" and new_status == "accepted":
            apply_patch(self.request, save=False, src=context.serialize())
            context.dateAccepted = get_now()
            context.acceptance = True
        elif (
            status in ["accepted", "stopping"]
            and new_status in ["declined", "satisfied"]
        ):
            apply_patch(self.request, save=False, src=context.serialize())
            context.dateDecision = get_now()
        elif (
            (old_rules and status in ["pending", "accepted", "stopping"])
            or (not old_rules and status == "accepted")
            and new_status == "stopped"
        ):
            apply_patch(self.request, save=False, src=context.serialize())
            context.dateDecision = get_now()
            context.dateCanceled = context.dateCanceled or get_now()
        else:
            raise_operation_error(
                self.request,
                "Can't update complaint from {} to {} status".format(status, new_status)
            )


class BaseTenderClaimResource(ComplaintAdminPatchMixin, BaseResource):
    patch_check_tender_excluded_statuses = (
        "draft", "claim", "answered",
    )
    patch_check_tender_statuses = (
        "active.qualification", "active.awarded",
    )
    patch_as_complaint_owner_tender_statuses = (
        "active.tendering",
    )

    @staticmethod
    def validate_submit_claim_time_method(request):
        raise NotImplementedError

    @staticmethod
    def validate_update_claim_time_method(request):
        raise NotImplementedError

    def pre_create(self):
        complaint = self.request.validated["complaint"]
        complaint.date = get_now()
        if complaint.status == "claim":
            self.validate_submit_claim_time_method(self.request)
            complaint.dateSubmitted = get_now()
        else:
            complaint.status = "draft"
        return complaint

    @json_view(
        content_type="application/json",
        validators=(
            validate_complaint_data,
            validate_complaint_operation_not_in_active_tendering,
            validate_add_complaint_with_tender_cancellation_in_pending,
            validate_add_complaint_with_lot_cancellation_in_pending("complaint"),
        ),
        permission="create_complaint",
    )
    def collection_post(self):
        """Post a complaint for award
        """
        tender = self.request.validated["tender"]

        complaint = self.pre_create()

        complaint.complaintID = "{}.{}{}".format(
            tender.tenderID,
            self.server_id,
            calculate_total_complaints(tender) + 1
        )
        access = set_ownership(complaint, self.request)
        self.context.complaints.append(complaint)
        if save_tender(self.request):
            self.LOGGER.info(
                "Created tender award complaint {}".format(complaint.id),
                extra=context_unpack(
                    self.request, {"MESSAGE_ID": "tender_complaint_create"}, {"complaint_id": complaint.id}
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tender Claims".format(tender.procurementMethodType),
                tender_id=tender.id,
                complaint_id=complaint.id,
            )
            return {"data": complaint.serialize(tender.status), "access": access}

    @json_view(
        content_type="application/json",
        permission="edit_complaint",
        validators=(
            validate_patch_complaint_data,
            validate_complaint_update_with_cancellation_lot_pending,
            validate_complaint_operation_not_in_active_tendering,
            validate_update_complaint_not_in_allowed_claim_status,
            validate_operation_with_lot_cancellation_in_pending("complaint"),
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
        if (
            self.patch_check_tender_excluded_statuses != "__all__"
            and self.context.status not in self.patch_check_tender_excluded_statuses
            and self.request.validated["tender"].status in self.patch_check_tender_statuses
        ):
            check_tender_status(self.request)

        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender award complaint {}".format(self.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_award_complaint_patch"}),
            )
            return {"data": self.context.serialize("view")}

    def patch_as_complaint_owner(self, data):
        context = self.context
        status = self.context.status
        new_status = data.get("status", status)

        tender = self.request.validated["tender"]

        if (
            new_status == "cancelled"
            and status in ["draft", "claim", "answered"]
        ):
            apply_patch(self.request, save=False, src=context.serialize())
            context.dateCanceled = get_now()

        elif (
            tender.status in self.patch_as_complaint_owner_tender_statuses
            and status == "draft"
            and new_status == status
        ):
            apply_patch(self.request, save=False, src=context.serialize())
        elif (
            tender.status in self.patch_as_complaint_owner_tender_statuses
            and status == "draft"
            and new_status == "claim"
        ):
            self.validate_submit_claim_time_method(self.request)
            apply_patch(self.request, save=False, src=context.serialize())
            context.dateSubmitted = get_now()

        elif status == "answered" and new_status == status:
            apply_patch(self.request, save=False, src=context.serialize())
        elif (
            status == "answered"
            and new_status == "resolved"
            and self.check_satisfied(data)
        ):
            apply_patch(self.request, save=False, src=context.serialize())
        else:
            raise_operation_error(
                self.request,
                "Can't update complaint from {} to {} status".format(status, new_status)
            )

    def patch_as_tender_owner(self, data):
        context = self.context
        status = context.status
        new_status = data.get("status", status)

        if status == "claim" and new_status == status:
            self.validate_update_claim_time_method(self.request)
            apply_patch(self.request, save=False, src=context.serialize())

        elif (
            status == "claim"
            and data.get("resolution", context.resolution)
            and data.get("resolutionType", context.resolutionType)
            and new_status == "answered"
        ):
            self.validate_update_claim_time_method(self.request)
            if len(data.get("resolution", context.resolution)) < 20:
                raise_operation_error(self.request, "Can't update complaint: resolution too short")
            apply_patch(self.request, save=False, src=context.serialize())
            context.dateAnswered = get_now()
        else:
            raise_operation_error(
                self.request,
                "Can't update complaint from {} to {} status".format(status, new_status)
            )

    def patch_as_abovethresholdreviewers(self, data):
        raise_operation_error(self.request, "Forbidden")

    def check_satisfied(self, data):
        satisfied = data.get("satisfied", self.context.satisfied)
        return satisfied is True
