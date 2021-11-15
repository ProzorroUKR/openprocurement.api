# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    context_unpack, 
    json_view, 
    set_ownership, 
    raise_operation_error,
    get_first_revision_date,
    get_now
)
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.core.validation import (
    validate_complaint_data,
    validate_patch_complaint_data,
    validate_award_complaint_add_only_for_active_lots,
    validate_update_complaint_not_in_allowed_complaint_status,
    validate_update_complaint_not_in_allowed_claim_status,
)
from openprocurement.tender.core.utils import apply_patch, save_tender, calculate_total_complaints
from openprocurement.tender.cfaua.views.award_complaint import TenderEUAwardComplaintResource, TenderEUAwardClaimResource
from openprocurement.tender.core.views.award_complaint import get_bid_id
from openprocurement.tender.core.views.complaint import (
    BaseComplaintGetResource
)
from openprocurement.tender.cfaua.utils import qualifications_resource
from openprocurement.tender.cfaua.validation import (
    validate_add_complaint_not_in_pre_qualification,
    validate_update_complaint_not_in_pre_qualification,
    validate_add_complaint_not_in_qualification_period,
    validate_update_qualification_complaint_only_for_active_lots,
)


@qualifications_resource(
    name="closeFrameworkAgreementUA:Tender Qualification Complaints Get",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    request_method=["GET"],
    description="Tender EU qualification complaints get",
)
class TenderEUQualificationComplaintGetResource(BaseComplaintGetResource):
    """ """


@qualifications_resource(
    name="closeFrameworkAgreementUA:Tender Qualification Complaints",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender EU qualification complaints",
)
class TenderEUQualificationComplaintResource(TenderEUAwardComplaintResource):
    def complaints_len(self, tender):
        return sum(
            [len(i.complaints) for i in tender.awards],
            sum([len(i.complaints) for i in tender.qualifications], len(tender.complaints)),
        )

    @json_view(
        content_type="application/json",
        permission="create_qualification_complaint",
        validators=(
            validate_complaint_data,
            validate_add_complaint_not_in_pre_qualification,
            validate_award_complaint_add_only_for_active_lots,
            validate_add_complaint_not_in_qualification_period,
        ),
    )
    def collection_post(self):
        """Post a complaint
        """
        tender = self.request.validated["tender"]
        old_rules = get_first_revision_date(tender) < RELEASE_2020_04_19

        complaint = self.request.validated["complaint"]
        complaint.relatedLot = self.context.lotID
        complaint.date = get_now()
        complaint.bid_id = get_bid_id(self.request)
        if old_rules and complaint.status == "pending":
            complaint.dateSubmitted = get_now()
        else:
            complaint.status = "draft"
        complaint.complaintID = "{}.{}{}".format(
            tender.tenderID,
            self.server_id,
            calculate_total_complaints(tender) + 1,
        )
        access = set_ownership(complaint, self.request)
        self.context.complaints.append(complaint)
        if save_tender(self.request):
            self.LOGGER.info(
                "Created tender qualification complaint {}".format(complaint.id),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "tender_qualification_complaint_create"},
                    {"complaint_id": complaint.id},
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tender Qualification Complaints".format(tender.procurementMethodType),
                tender_id=tender.id,
                qualification_id=self.request.validated["qualification_id"],
                complaint_id=complaint["id"],
            )
            return {"data": complaint.serialize("view"), "access": access}

    @json_view(
        content_type="application/json",
        permission="edit_complaint",
        validators=(
            validate_patch_complaint_data,
            validate_update_complaint_not_in_pre_qualification,
            validate_update_qualification_complaint_only_for_active_lots,
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
                "Updated tender qualification complaint {}".format(self.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_qualification_complaint_patch"}),
            )
            return {"data": self.context.serialize("view")}

    def patch_as_complaint_owner(self, data):
        tender = self.request.validated["tender"]
        data = self.request.validated["data"]
        status = self.context.status
        new_status = data.get("status", status)

        is_qualificationPeriod = tender.qualificationPeriod.startDate < get_now() and (
            not tender.qualificationPeriod.endDate or tender.qualificationPeriod.endDate > get_now()
        )

        apply_rules_2020_04_19 = get_first_revision_date(tender, get_now()) > RELEASE_2020_04_19

        if (
            new_status == "cancelled"
            and status == "draft"
            and not apply_rules_2020_04_19
        ):
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateCanceled = get_now()
        elif (
            apply_rules_2020_04_19
            and status == "draft"
            and new_status == "mistaken"
        ):
            self.context.rejectReason = "cancelledByComplainant"
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif (
            status in ["pending", "accepted"]
            and new_status == "stopping"
            and not apply_rules_2020_04_19
        ):
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateCanceled = get_now()
        elif (
            is_qualificationPeriod
            and status == "draft"
            and new_status == status
        ):
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif (
            is_qualificationPeriod
            and status == "draft"
            and new_status == "pending"
            and not apply_rules_2020_04_19
        ):
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateSubmitted = get_now()
        else:
            raise_operation_error(
                self.request,
                "Can't update complaint from {} to {} status".format(status, new_status)
            )

    def patch_as_tender_owner(self, data):
        data = self.request.validated["data"]
        status = self.context.status
        new_status = data.get("status", status)

        if status in ["pending", "accepted"]:
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif (
            status == "satisfied"
            and new_status == status
        ):
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif (
            status == "satisfied"
            and data.get("tendererAction", self.context.tendererAction)
            and new_status == "resolved"
        ):
            apply_patch(self.request, save=False, src=self.context.serialize())
        else:
            raise_operation_error(
                self.request,
                "Can't update complaint from {} to {} status".format(status, new_status)
            )

    def patch_as_abovethresholdreviewers(self, data):
        tender = self.request.validated["tender"]
        data = self.request.validated["data"]
        status = self.context.status
        new_status = data.get("status", status)

        apply_rules_2020_04_19 = get_first_revision_date(tender, get_now()) > RELEASE_2020_04_19

        if (
            self.request.authenticated_role == "aboveThresholdReviewers"
            and status in ["pending", "accepted", "stopping"]
            and new_status == status
        ):
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif (
            self.request.authenticated_role == "aboveThresholdReviewers"
            and status in ["pending", "stopping"]
            and (
                (not apply_rules_2020_04_19 and new_status in ["invalid", "mistaken"])
                or (new_status == "invalid")
            )
        ):
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateDecision = get_now()
            self.context.acceptance = False
        elif (
            self.request.authenticated_role == "aboveThresholdReviewers"
            and status == "pending"
            and new_status == "accepted"
        ):
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateAccepted = get_now()
            self.context.acceptance = True
        elif (
            self.request.authenticated_role == "aboveThresholdReviewers"
            and status in ["accepted", "stopping"]
            and new_status == "declined"
        ):
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateDecision = get_now()
        elif (
            self.request.authenticated_role == "aboveThresholdReviewers"
            and status in ["accepted", "stopping"]
            and new_status == "satisfied"
        ):
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateDecision = get_now()
            tender.status = "active.pre-qualification"
            if tender.qualificationPeriod.endDate:
                tender.qualificationPeriod.endDate = None
        elif (
            self.request.authenticated_role == "aboveThresholdReviewers"
            and ((not apply_rules_2020_04_19 and status in ["pending", "accepted", "stopping"])
                 or (apply_rules_2020_04_19 and status == "accepted"))
            and new_status == "stopped"
        ):
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateDecision = get_now()
            self.context.dateCanceled = self.context.dateCanceled or get_now()
        else:
            raise_operation_error(
                self.request,
                "Can't update complaint from {} to {} status".format(status, new_status)
            )


@qualifications_resource(
    name="closeFrameworkAgreementUA:Tender Qualification Claims",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender EU qualification claims",
)
class TenderEUQualificationClaimResource(TenderEUAwardClaimResource):
    def complaints_len(self, tender):
        return sum(
            [len(i.complaints) for i in tender.awards],
            sum([len(i.complaints) for i in tender.qualifications], len(tender.complaints)),
        )

    @json_view(
        content_type="application/json",
        permission="create_qualification_complaint",
        validators=(
            validate_complaint_data,
            validate_add_complaint_not_in_pre_qualification,
            validate_award_complaint_add_only_for_active_lots,
            validate_add_complaint_not_in_qualification_period,
        ),
    )
    def collection_post(self):
        """Post a complaint
        """
        tender = self.request.validated["tender"]

        complaint = self.request.validated["complaint"]
        complaint.relatedLot = self.context.lotID
        complaint.date = get_now()
        complaint.bid_id = get_bid_id(self.request)
        if complaint.status == "claim":
            complaint.dateSubmitted = get_now()
        else:
            complaint.status = "draft"
        if (
            self.context.status == "unsuccessful"
            and complaint.status == "claim"
            and self.context.bidID != complaint.bid_id
        ):
            raise_operation_error(self.request, "Can add claim only on unsuccessful qualification of your bid")
        complaint.complaintID = "{}.{}{}".format(
            tender.tenderID,
            self.server_id,
            calculate_total_complaints(tender) + 1,
        )
        access = set_ownership(complaint, self.request)
        self.context.complaints.append(complaint)
        if save_tender(self.request):
            self.LOGGER.info(
                "Created tender qualification complaint {}".format(complaint.id),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "tender_qualification_complaint_create"},
                    {"complaint_id": complaint.id},
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tender Qualification Claims".format(tender.procurementMethodType),
                tender_id=tender.id,
                qualification_id=self.request.validated["qualification_id"],
                complaint_id=complaint["id"],
            )
            return {"data": complaint.serialize("view"), "access": access}

    @json_view(
        content_type="application/json",
        permission="edit_complaint",
        validators=(
            validate_patch_complaint_data,
            validate_update_complaint_not_in_pre_qualification,
            validate_update_qualification_complaint_only_for_active_lots,
            validate_update_complaint_not_in_allowed_claim_status,
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
                "Updated tender qualification complaint {}".format(self.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_qualification_complaint_patch"}),
            )
            return {"data": self.context.serialize("view")}

    def patch_as_complaint_owner(self, data):
        tender = self.request.validated["tender"]
        data = self.request.validated["data"]
        status = self.context.status
        new_status = data.get("status", status)

        is_qualificationPeriod = tender.qualificationPeriod.startDate < get_now() and (
            not tender.qualificationPeriod.endDate or tender.qualificationPeriod.endDate > get_now()
        )

        if (
            new_status == "cancelled"
            and status in ["draft", "claim", "answered"]
        ):
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateCanceled = get_now()
        elif (
            is_qualificationPeriod
            and status == "draft"
            and new_status == status
        ):
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif (
            is_qualificationPeriod
            and status == "draft"
            and new_status == "claim"
        ):
            if (
                self.request.validated["qualification"].status == "unsuccessful"
                and self.request.validated["qualification"].bidID != self.context.bid_id
            ):
                raise_operation_error(self.request, "Can add claim only on unsuccessful qualification of your bid")
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateSubmitted = get_now()

        elif (
            status == "answered"
            and new_status == status
        ):
            apply_patch(self.request, save=False, src=self.context.serialize())
        else:
            raise_operation_error(
                self.request,
                "Can't update complaint from {} to {} status".format(status, new_status)
            )

    def patch_as_tender_owner(self, data):
        data = self.request.validated["data"]
        status = self.context.status
        new_status = data.get("status", status)

        if (
            status == "claim"
            and new_status == status
        ):
            apply_patch(self.request, save=False, src=self.context.serialize())
        elif (
            status == "claim"
            and data.get("resolution", self.context.resolution)
            and data.get("resolutionType", self.context.resolutionType)
            and new_status == "answered"
        ):
            if len(data.get("resolution", self.context.resolution)) < 20:
                raise_operation_error(self.request, "Can't update complaint: resolution too short")
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateAnswered = get_now()
        else:
            raise_operation_error(
                self.request,
                "Can't update complaint from {} to {} status".format(status, new_status)
            )

    def patch_as_abovethresholdreviewers(self, data):
        raise_operation_error(self.request, "Forbidden")
