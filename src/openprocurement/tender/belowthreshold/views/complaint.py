# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    get_now,
    json_view,
    raise_operation_error
)
from openprocurement.api.constants import RELEASE_2020_04_19

from openprocurement.tender.core.views.complaint import BaseTenderComplaintResource
from openprocurement.tender.core.utils import optendersresource, apply_patch, get_first_revision_date
from openprocurement.tender.core.validation import validate_complaint_data, validate_patch_complaint_data

from openprocurement.tender.belowthreshold.validation import (
    validate_update_complaint_not_in_allowed_status,
    validate_add_complaint_not_in_allowed_tender_status,
    validate_update_complaint_not_in_allowed_tender_status,
    validate_only_claim_allowed,
)


@optendersresource(
    name="belowThreshold:Tender Complaints",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="belowThreshold",
    description="Tender complaints",
)
class TenderComplaintResource(BaseTenderComplaintResource):

    patch_check_tender_excluded_statuses = ("draft", "claim", "answered")

    def pre_create(self):
        complaint = self.request.validated["complaint"]
        complaint.date = get_now()
        if complaint.status == "claim":
            complaint.dateSubmitted = get_now()
        else:
            complaint.status = "draft"

        return complaint

    @json_view(
        content_type="application/json",
        validators=(
            validate_complaint_data,
            validate_only_claim_allowed,
            validate_add_complaint_not_in_allowed_tender_status
        ),
        permission="create_complaint",
    )
    def collection_post(self):
        """Post a complaint
        """
        return super(TenderComplaintResource, self).collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_complaint_data,
            validate_update_complaint_not_in_allowed_tender_status,
            validate_update_complaint_not_in_allowed_status,
        ),
        permission="edit_complaint",
    )
    def patch(self):
        return super(TenderComplaintResource, self).patch()

    def patch_as_complaint_owner(self, data):
        context = self.context
        status = self.context.status
        new_status = data.get("status", status)

        tender = self.request.validated["tender"]

        if status in ["draft", "claim", "answered"] and new_status == "cancelled":
            apply_patch(self.request, save=False, src=context.serialize())
            context.dateCanceled = get_now()
        elif (
            get_first_revision_date(tender, get_now()) > RELEASE_2020_04_19
            and new_status == "mistaken"
        ):
            context.rejectReason = "cancelledByComplainant"
            apply_patch(self.request, save=False, src=context.serialize())
        elif (
            tender.status in ["active.enquiries", "active.tendering"]
            and status == "draft"
            and new_status == status
        ):
            apply_patch(self.request, save=False, src=context.serialize())
        elif (
            tender.status in ["active.enquiries", "active.tendering"]
            and status == "draft"
            and new_status == "claim"
        ):
            apply_patch(self.request, save=False, src=context.serialize())
            context.dateSubmitted = get_now()
        elif status == "answered" and new_status == status:
            apply_patch(self.request, save=False, src=context.serialize())
        elif (
            status == "answered"
            and isinstance(data.get("satisfied", context.satisfied), bool)
            and new_status == "resolved"
        ):
            apply_patch(self.request, save=False, src=context.serialize())

    def patch_as_tender_owner(self, data):
        context = self.context
        status = self.context.status
        new_status = data.get("status", status)

        if status == "claim" and new_status == status:
            apply_patch(self.request, save=False, src=context.serialize())
        elif (
            status == "claim"
            and data.get("resolution", context.resolution)
            and data.get("resolutionType", context.resolutionType)
            and new_status == "answered"
        ):
            if len(data.get("resolution", context.resolution)) < 20:
                raise_operation_error(self.request, "Can't update complaint: resolution too short")
            apply_patch(self.request, save=False, src=context.serialize())
            context.dateAnswered = get_now()

    def patch_as_abovethresholdreviewers(self, data):
        raise_operation_error(self.request, "Forbidden")
