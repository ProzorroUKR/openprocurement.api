# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    get_now,
    json_view,
    raise_operation_error,
    get_first_revision_date,
)
from openprocurement.tender.core.validation import (
    validate_complaint_data,
    validate_patch_complaint_data,
    validate_add_complaint_not_in_complaint_period,
    validate_award_complaint_add_only_for_active_lots,
    validate_award_complaint_update_only_for_active_lots,
    validate_award_complaint_operation_not_in_allowed_status,
)
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.core.views.award_complaint import BaseTenderAwardComplaintResource
from openprocurement.tender.core.utils import optendersresource, apply_patch
from openprocurement.tender.belowthreshold.validation import validate_award_complaint_update_not_in_allowed_status


@optendersresource(
    name="belowThreshold:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="belowThreshold",
    description="Tender award complaints",
)
class TenderAwardComplaintResource(BaseTenderAwardComplaintResource):
    patch_check_tender_excluded_statuses = ("draft", "claim", "answered")

    def pre_create(self):
        complaint = self.request.validated["complaint"]
        complaint.date = get_now()
        complaint.relatedLot = self.context.lotID
        if complaint.status == "claim":
            complaint.dateSubmitted = get_now()
        else:
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
        ),
    )
    def collection_post(self):
        return super(TenderAwardComplaintResource, self).collection_post()

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
        return super(TenderAwardComplaintResource, self).patch()

    def patch_as_complaint_owner(self, data):
        complaint_period = self.request.validated["award"].complaintPeriod
        is_complaint_period = (
            complaint_period.startDate <= get_now() <= complaint_period.endDate
            if complaint_period.endDate
            else complaint_period.startDate <= get_now()
        )

        tender = self.request.validated["tender"]
        context = self.context
        status = context.status
        new_status = data.get("status", status)

        if status in ["draft", "claim", "answered"] and new_status == "cancelled":
            apply_patch(self.request, save=False, src=context.serialize())
            context.dateCanceled = get_now()
        elif status == "draft":

            if not is_complaint_period:
                raise_operation_error(self.request, "Can't update draft complaint not in complaintPeriod")

            if new_status == status:
                apply_patch(self.request, save=False, src=context.serialize())
            elif (
                get_first_revision_date(tender, get_now()) > RELEASE_2020_04_19
                and new_status == "mistaken"
            ):
                context.rejectReason = "cancelledByComplainant"
                apply_patch(self.request, save=False, src=context.serialize())
            elif new_status == "claim":
                apply_patch(self.request, save=False, src=context.serialize())
                context.dateSubmitted = get_now()
            else:
                raise_operation_error(self.request, "Can't update draft complaint to {} status".format(new_status))

        elif status == "answered" and new_status == status:
            apply_patch(self.request, save=False, src=context.serialize())

        elif status == "answered" and new_status == "resolved":
            if not isinstance(data.get("satisfied", context.satisfied), bool):
                raise_operation_error(self.request, "Can't resolve answered claim: satisfied required")

            apply_patch(self.request, save=False, src=context.serialize())
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
    
    def patch_as_abovethresholdreviewers(self, data):
        raise_operation_error(self.request, "Forbidden")
