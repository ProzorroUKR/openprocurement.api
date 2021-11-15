# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    get_now,
    json_view,
    raise_operation_error
)

from openprocurement.tender.core.views.complaint import BaseTenderClaimResource
from openprocurement.tender.core.views.complaint import BaseComplaintGetResource
from openprocurement.tender.core.utils import optendersresource, apply_patch
from openprocurement.tender.core.validation import validate_complaint_data, validate_patch_complaint_data

from openprocurement.tender.belowthreshold.validation import (
    validate_update_complaint_not_in_allowed_status,
    validate_add_complaint_not_in_allowed_tender_status,
    validate_update_complaint_not_in_allowed_tender_status,
)


@optendersresource(
    name="belowThreshold:Tender Complaints Get",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="belowThreshold",
    request_method=["GET"],
    description="Tender complaints get",
)
class TenderComplaintGetResource(BaseComplaintGetResource):
    """ """


@optendersresource(
    name="belowThreshold:Tender Claims",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="belowThreshold",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender claims",
)
class TenderClaimResource(BaseTenderClaimResource):

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
            validate_add_complaint_not_in_allowed_tender_status
        ),
        permission="create_complaint",
    )
    def collection_post(self):
        """Post a complaint
        """
        return super(TenderClaimResource, self).collection_post()

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
        return super(TenderClaimResource, self).patch()

    def patch_as_complaint_owner(self, data):
        context = self.context
        status = self.context.status
        new_status = data.get("status", status)

        tender = self.request.validated["tender"]

        if status in ["draft", "claim", "answered"] and new_status == "cancelled":
            apply_patch(self.request, save=False, src=context.serialize())
            context.dateCanceled = get_now()
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
            # TODO why not implemented validate_submit_claim_time_method?
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
