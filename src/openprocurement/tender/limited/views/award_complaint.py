# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    get_now, 
    context_unpack, 
    json_view, 
    set_ownership, 
    raise_operation_error,
    get_first_revision_date,
    get_now,
)
from openprocurement.api.constants import RELEASE_2020_04_19

from openprocurement.tender.core.utils import apply_patch, save_tender, optendersresource

from openprocurement.tender.core.validation import (
    validate_add_complaint_not_in_complaint_period,
    validate_update_complaint_not_in_allowed_complaint_status,
)

from openprocurement.tender.limited.validation import (
    validate_complaint_data,
    validate_patch_complaint_data,
    validate_award_complaint_operation_not_in_active,
)

from openprocurement.tender.belowthreshold.views.award_complaint import TenderAwardComplaintResource


@optendersresource(
    name="negotiation:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="negotiation",
    description="Tender negotiation award complaints",
)
class TenderNegotiationAwardComplaintResource(TenderAwardComplaintResource):
    @json_view(
        content_type="application/json",
        permission="create_award_complaint",
        validators=(
            validate_complaint_data,
            validate_award_complaint_operation_not_in_active,
            validate_add_complaint_not_in_complaint_period,
        ),
    )
    def collection_post(self):
        """Post a complaint for award
        """
        tender = self.request.validated["tender"]
        complaint = self.request.validated["complaint"]
        complaint.date = get_now()
        complaint.type = "complaint"
        if complaint.status == "pending":
            complaint.dateSubmitted = get_now()
        else:
            complaint.status = "draft"
        complaint.complaintID = "{}.{}{}".format(
            tender.tenderID, self.server_id, sum([len(i.complaints) for i in tender.awards], 1)
        )
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
            validate_award_complaint_operation_not_in_active,
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
        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender award complaint {}".format(self.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_award_complaint_patch"}),
            )
            return {"data": self.context.serialize("view")}

    def patch_as_complaint_owner(self, data):
        complaint_period = self.request.validated["award"].complaintPeriod
        is_complaint_period = (
            complaint_period.startDate < get_now() < complaint_period.endDate
            if complaint_period.endDate
            else complaint_period.startDate < get_now()
        )
        status = self.context.status
        new_status = data.get("status", status)

        tender = self.request.validated["tender"]

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
                get_first_revision_date(tender) > RELEASE_2020_04_19 
                and new_status == "mistaken"
            ):
                apply_patch(self.request, save=False, src=self.context.serialize())
            elif new_status == "pending":
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
        
        if status in ["pending", "accepted", "stopping"] and new_status == status:
            apply_patch(self.request, save=False, src=self.context.serialize())

        elif (
            status in ["pending", "stopping"] 
            and (
                (not get_first_revision_date(tender) > RELEASE_2020_04_19 and new_status in ["invalid", "mistaken"]) 
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

        elif status in ["pending", "accepted", "stopping"] and new_status == "stopped":
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
