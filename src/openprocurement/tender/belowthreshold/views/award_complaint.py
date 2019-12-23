# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    get_now,
    context_unpack,
    json_view,
    set_ownership,
    APIResource,
    raise_operation_error,
)
from openprocurement.tender.core.validation import (
    validate_complaint_data,
    validate_patch_complaint_data,
    validate_add_complaint_not_in_complaint_period,
    validate_award_complaint_add_only_for_active_lots,
    validate_award_complaint_update_only_for_active_lots,
    validate_award_complaint_operation_not_in_allowed_status,
)
from openprocurement.tender.belowthreshold.utils import check_tender_status
from openprocurement.tender.core.utils import save_tender, optendersresource, apply_patch
from openprocurement.tender.belowthreshold.validation import validate_award_complaint_update_not_in_allowed_status


@optendersresource(
    name="belowThreshold:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="belowThreshold",
    description="Tender award complaints",
)
class TenderAwardComplaintResource(APIResource):
    @json_view(
        content_type="application/json",
        permission="create_award_complaint",
        validators=(
            validate_complaint_data,
            validate_award_complaint_operation_not_in_allowed_status,
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
        if complaint.status == "claim":
            complaint.dateSubmitted = get_now()
        else:
            complaint.status = "draft"
        complaint.complaintID = "{}.{}{}".format(
            tender.tenderID, self.server_id, sum([len(i.complaints) for i in tender.awards], len(tender.complaints)) + 1
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

    @json_view(permission="view_tender")
    def collection_get(self):
        """List complaints for award
        """
        return {"data": [i.serialize("view") for i in self.context.complaints]}

    @json_view(permission="view_tender")
    def get(self):
        """Retrieving the complaint for award
        """
        return {"data": self.context.serialize("view")}

    @json_view(
        content_type="application/json",
        permission="edit_complaint",
        validators=(
            validate_patch_complaint_data,
            validate_award_complaint_operation_not_in_allowed_status,
            validate_award_complaint_update_only_for_active_lots,
            validate_award_complaint_update_not_in_allowed_status,
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

        if self.context.tendererAction and not self.context.tendererActionDate:  # not sure we need this
            self.context.tendererActionDate = get_now()
            
        if (
            self.context.status not in ["draft", "claim", "answered"]
            and self.request.validated["tender"].status in ["active.qualification", "active.awarded"]
        ):
            check_tender_status(self.request)

        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender award complaint {}".format(self.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_award_complaint_patch"}),
            )
            return {"data": self.context.serialize("view")}

    def patch_as_complaint_owner(self, data):
        status = self.context.status
        new_status = data.get("status", status)

        if status in ["draft", "claim", "answered"] and new_status == "cancelled":
            apply_patch(self.request, save=False, src=self.context.serialize())
            self.context.dateCanceled = get_now()
        elif status == "draft":
            complaint_period = self.request.validated["award"].complaintPeriod
            is_complaint_period = (
                complaint_period.startDate < get_now() < complaint_period.endDate
                if complaint_period.endDate
                else complaint_period.startDate < get_now()
            )
            if not is_complaint_period:
                raise_operation_error(self.request, "Can't update draft complaint not in complaintPeriod")

            if new_status == status:
                apply_patch(self.request, save=False, src=self.context.serialize())
            elif new_status == "claim":
                apply_patch(self.request, save=False, src=self.context.serialize())
                self.context.dateSubmitted = get_now()
            else:
                raise_operation_error(self.request, "Can't update draft complaint to {} status".format(new_status))

        elif status == "answered" and new_status == status:
            apply_patch(self.request, save=False, src=self.context.serialize())

        elif status == "answered" and new_status == "resolved":
            if not isinstance(data.get("satisfied", self.context.satisfied), bool):
                raise_operation_error(self.request, "Can't resolve answered claim: satisfied required")

            apply_patch(self.request, save=False, src=self.context.serialize())
        else:
            raise_operation_error(self.request, "Can't update complaint from {} to {}".format(status, new_status))

    def patch_as_tender_owner(self, data):
        context = self.context
        status = context.status
        new_status = data.get("status", status)
        
        if status == "claim" and new_status == status:
            apply_patch(self.request, save=False, src=context.serialize())

        elif status == "claim" and new_status == "answered":
            if not data.get("resolution", context.resolution) or not data.get("resolutionType", context.resolutionType):
                raise_operation_error(self.request, "Can't answer complaint: resolution and resolutionType required")

            if len(data.get("resolution", context.resolution or "")) < 20:
                raise_operation_error(self.request, "Can't update complaint: resolution too short")

            apply_patch(self.request, save=False, src=context.serialize())
            context.dateAnswered = get_now()
        else:
            raise_operation_error(self.request, "Can't update complaint from {} to {}".format(status, new_status))
