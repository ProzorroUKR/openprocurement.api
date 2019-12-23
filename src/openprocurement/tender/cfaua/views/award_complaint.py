# -*- coding: utf-8 -*-
from openprocurement.api.utils import get_now, context_unpack, json_view, raise_operation_error, set_ownership
from openprocurement.tender.core.validation import (
    validate_complaint_data,
    validate_patch_complaint_data,
    validate_award_complaint_add_only_for_active_lots,
    validate_award_complaint_update_only_for_active_lots,
    validate_update_complaint_not_in_allowed_complaint_status,
)
from openprocurement.tender.core.utils import apply_patch, optendersresource, save_tender
from openprocurement.tender.openua.views.award_complaint import TenderUaAwardComplaintResource, get_bid_id

from openprocurement.tender.cfaua.utils import check_tender_status_on_active_qualification_stand_still
from openprocurement.tender.cfaua.validation import (
    validate_add_complaint_not_in_complaint_period,
    validate_update_complaint_not_in_qualification,
    validate_add_complaint_not_in_qualification_stand_still,
)


@optendersresource(
    name="closeFrameworkAgreementUA:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender EU award complaints",
)
class TenderEUAwardComplaintResource(TenderUaAwardComplaintResource):
    def complaints_len(self, tender):
        return sum(
            [len(i.complaints) for i in tender.awards],
            sum([len(i.complaints) for i in tender.qualifications], len(tender.complaints)),
        )

    @json_view(
        content_type="application/json",
        permission="create_award_complaint",
        validators=(
            validate_complaint_data,
            validate_add_complaint_not_in_qualification_stand_still,
            validate_award_complaint_add_only_for_active_lots,
            validate_add_complaint_not_in_complaint_period,
        ),
    )
    def collection_post(self):
        """Post a complaint for award
        """
        tender = self.request.validated["tender"]
        complaint = self.request.validated["complaint"]
        complaint.date = get_now()
        complaint.relatedLot = self.context.lotID
        complaint.bid_id = get_bid_id(self.request)

        if complaint.status == "claim":
            self.validate_posting_claim()
            complaint.dateSubmitted = get_now()
        elif complaint.status == "pending":
            complaint.type = "complaint"
            complaint.dateSubmitted = get_now()
        else:
            complaint.status = "draft"

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
            validate_update_complaint_not_in_qualification,
            validate_award_complaint_update_only_for_active_lots,
            validate_update_complaint_not_in_allowed_complaint_status,
        ),
    )
    def patch(self):
        """Patch a complaint for award
        """
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
            and self.request.validated["tender"].status == "active.qualification.stand-still"
        ):
            check_tender_status_on_active_qualification_stand_still(self.request)

        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender award complaint {}".format(self.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_award_complaint_patch"}),
            )
            return {"data": self.context.serialize("view")}

    def validate_posting_complaint(self):
        """
        we overwrite checking an active award
        as long as we have "validate_add_complaint_not_in_qualification_stand_still"
        in qualification.stand-still we always have an active award
        """

    def on_satisfy_complaint_by_reviewer(self):
        tender = self.request.validated["tender"]
        tender.status = "active.qualification"
        if tender.awardPeriod.endDate:
            tender.awardPeriod.endDate = None
