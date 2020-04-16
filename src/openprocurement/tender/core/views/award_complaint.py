# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.complaint import BaseTenderComplaintResource
from openprocurement.api.utils import (
    get_now, 
    context_unpack, 
    json_view, 
    set_ownership, 
    raise_operation_error,
    get_first_revision_date,
)
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.core.validation import (
    validate_complaint_data,
    validate_patch_complaint_data,
    validate_add_complaint_not_in_complaint_period,
    validate_award_complaint_add_only_for_active_lots,
    validate_award_complaint_update_only_for_active_lots,
    validate_award_complaint_operation_not_in_allowed_status,
    validate_update_complaint_not_in_allowed_complaint_status,
    validate_complaint_type_change,
    validate_update_award_with_cancellation_lot_pending,
    validate_add_complaint_with_tender_cancellation_in_pending,
    validate_add_complaint_with_lot_cancellation_in_pending
)
from openprocurement.tender.belowthreshold.utils import check_tender_status
from openprocurement.tender.core.utils import save_tender, apply_patch


def get_bid_id(request):
    if request.authenticated_role != "bid_owner":
        return
    tender = request.validated["tender"]
    bids = {"{}_{}".format(i.owner, i.owner_token): i.id for i in tender.bids}
    common = set(request.effective_principals).intersection(set(bids))
    if common:
        return bids[common.pop()]


class BaseTenderAwardComplaintResource(BaseTenderComplaintResource):
    patch_check_tender_excluded_statuses = (
        "draft", "claim", "answered", "pending", "accepted", "satisfied", "stopping",
    )

    @staticmethod
    def check_tender_status_method(request):
        return check_tender_status(request)

    def validate_posting_complaint(self):
        tender = self.request.validated["tender"]

        apply_rules_2020_04_19 = get_first_revision_date(tender, get_now()) > RELEASE_2020_04_19

        context_award = self.request.validated["award"]

        if not apply_rules_2020_04_19:

            if not any(
                award.status == "active"
                for award in tender.awards
                if award.lotID == context_award.lotID
            ):
                raise_operation_error(self.request, "Complaint submission is allowed only after award activation.")
        else:

            if context_award.status not in ("active", "unsuccessful"):
                raise_operation_error(
                    self.request,
                    "Complaint submission is allowed only after award activation or unsuccessful award.",
                )

    def validate_posting_claim(self):
        complaint = self.request.validated["complaint"]
        award = self.request.validated["award"]
        if award.status == "unsuccessful" and award.bid_id != complaint.bid_id:
            raise_operation_error(self.request, "Can add claim only on unsuccessful award of your bid")
        if award.status == "pending":
            raise_operation_error(self.request, "Claim submission is not allowed on pending award")

    def pre_create(self):
        tender = self.request.validated["tender"]
        not_apply_rules_2020_04_19 = get_first_revision_date(tender) < RELEASE_2020_04_19

        complaint = self.request.validated["complaint"]
        complaint.date = get_now()
        complaint.relatedLot = self.context.lotID
        complaint.bid_id = get_bid_id(self.request)

        if complaint.status == "claim":   # claim
            self.validate_posting_claim()
            complaint.dateSubmitted = get_now()
        elif not_apply_rules_2020_04_19 and complaint.status == "pending":  # complaint
            self.validate_posting_complaint()
            complaint.type = "complaint"
            complaint.dateSubmitted = get_now()
        else:  # draft is neither claim nor complaint yet
            complaint.status = "draft"
        
        return complaint
    
    @json_view(
        content_type="application/json",
        permission="create_award_complaint",
        validators=(
            validate_complaint_data,
            validate_award_complaint_operation_not_in_allowed_status,
            validate_award_complaint_add_only_for_active_lots,
            validate_add_complaint_not_in_complaint_period,
            validate_add_complaint_with_tender_cancellation_in_pending,
            validate_add_complaint_with_lot_cancellation_in_pending("award"),
        ),
    )
    def collection_post(self):
        """Post a complaint for award
        """
        tender = self.request.validated["tender"]
        
        complaint = self.pre_create()
        
        complaint.complaintID = "{}.{}{}".format(tender.tenderID, self.server_id, self.complaints_len(tender) + 1)
        access = set_ownership(complaint, self.request)
        self.context.complaints.append(complaint)
        if save_tender(self.request):
            self.LOGGER.info(
                "Created tender award complaint {}".format(complaint.id),
                extra=context_unpack(
                    self.request, {"MESSAGE_ID": "tender_award_complaint_create"}, {"complaint_id": complaint.id}
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tender Award Complaints".format(tender.procurementMethodType),
                tender_id=tender.id,
                award_id=self.request.validated["award_id"],
                complaint_id=complaint["id"],
            )
            return {"data": complaint.serialize("view"), "access": access}

    @json_view(
        content_type="application/json",
        permission="edit_complaint",
        validators=(
            validate_patch_complaint_data,
            validate_update_award_with_cancellation_lot_pending,
            validate_award_complaint_operation_not_in_allowed_status,
            validate_award_complaint_update_only_for_active_lots,
            validate_update_complaint_not_in_allowed_complaint_status,
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
            self.context.status not in self.patch_check_tender_excluded_statuses
            and self.request.validated["tender"].status in self.patch_check_tender_statuses
        ):
            self.check_tender_status_method(self.request)

        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender award complaint {}".format(self.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_award_complaint_patch"}),
            )
            return {"data": self.context.serialize("view")}

    def patch_as_complaint_owner(self, data):
        status = self.context.status
        new_status = data.get("status", status)
        if (
            status in ["draft", "claim", "answered"] and new_status == "cancelled"
            or status in ["pending", "accepted"] and new_status == "stopping"
        ):
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateCanceled = get_now()
        elif status == "draft":
            self.patch_draft_as_complaint_owner(data)

        elif status == "answered" and new_status == status:
            apply_patch(self.request, save=False, src=self.context.serialize())

        else:
            raise_operation_error(
                self.request,
                "Can't update complaint from {} to {} status".format(status, new_status)
            )

    def patch_draft_as_complaint_owner(self, data):
        tender = self.request.validated["tender"]
        
        complaint_period = self.request.validated["award"].complaintPeriod
        is_complaint_period = (
            complaint_period.startDate <= get_now() <= complaint_period.endDate
            if complaint_period.endDate
            else complaint_period.startDate <= get_now()
        )
        if not is_complaint_period:
            raise_operation_error(self.request, "Can't update draft complaint not in complaintPeriod")

        new_rules = get_first_revision_date(tender, get_now()) > RELEASE_2020_04_19
        new_status = data.get("status", self.context.status)
        if new_status == self.context.status:
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif (
            new_rules
            and self.context.type == "complaint"
            and new_status == "mistaken"
        ):
            self.context.rejectReason = "cancelledByComplainant"
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif new_status == "claim":
            self.validate_posting_claim()
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateSubmitted = get_now()

        elif new_status == "pending" and not new_rules:
            self.validate_posting_complaint()
            validate_complaint_type_change(self.request)
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.type = "complaint"
            self.context.dateSubmitted = get_now()
        else:
            raise_operation_error(self.request, "Can't update draft complaint into {} status".format(new_status))

    def patch_as_tender_owner(self, data):
        context = self.context
        status = context.status
        new_status = data.get("status", status)

        if status in ["pending", "accepted"] or new_status == status and status in ["claim", "satisfied"]:
            apply_patch(self.request, save=False, src=context.serialize())

        elif status == "claim" and new_status == "answered":
            if not data.get("resolution", context.resolution) or not data.get("resolutionType", context.resolutionType):
                raise_operation_error(self.request, "Can't update complaint: resolution and resolutionType required")

            if len(data.get("resolution", context.resolution)) < 20:
                raise_operation_error(self.request, "Can't update complaint: resolution too short")
            apply_patch(self.request, save=False, src=context.serialize())
            context.dateAnswered = get_now()

        elif status == "satisfied" and new_status == "resolved":
            if not data.get("tendererAction", context.tendererAction):
                raise_operation_error(self.request, "Can't update complaint: tendererAction required")

            apply_patch(self.request, save=False, src=context.serialize())
        else:
            raise_operation_error(self.request,
                                  "Can't update complaint from {} to {} status".format(status, new_status))

    def patch_as_abovethresholdreviewers(self, data):
        context = self.context
        status = context.status
        new_status = data.get("status", status)

        tender = self.request.validated["tender"]

        apply_rules_2020_04_19 = get_first_revision_date(tender, get_now()) > RELEASE_2020_04_19

        if new_status == status and status in ["pending", "accepted", "stopping"]:
            apply_patch(self.request, save=False, src=context.serialize())

        elif (
            status in ["pending", "stopping"]
            and ((not apply_rules_2020_04_19 and new_status in ["invalid", "mistaken"])
            or (new_status == "invalid"))
        ):
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

        elif (
            (not apply_rules_2020_04_19 and status in ["pending", "accepted", "stopping"])
            or (apply_rules_2020_04_19 and status in ["accepted", "stopping"])
            and new_status == "stopped"
        ):
            apply_patch(self.request, save=False, src=context.serialize())
            context.dateDecision = get_now()
            context.dateCanceled = context.dateCanceled or get_now()
        else:
            raise_operation_error(self.request,
                                  "Can't update complaint from {} to {} status".format(status, new_status))

    def on_satisfy_complaint_by_reviewer(self):
        pass
