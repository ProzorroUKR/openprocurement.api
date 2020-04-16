# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.cancellation import BaseTenderCancellationResource
from openprocurement.tender.openua.validation import validate_not_only_unsuccessful_awards_or_qualifications
from openprocurement.tender.core.validation import (
    validate_tender_not_in_terminated_status,
    validate_cancellation_data,
    validate_patch_cancellation_data,
    validate_cancellation_of_active_lot,
    validate_cancellation_status_with_complaints,
    # validate_cancellation_statuses,
    validate_create_cancellation_in_active_auction,
    validate_operation_cancellation_in_complaint_period,
    validate_operation_cancellation_permission,
)
from openprocurement.tender.openua.utils import CancelTenderLot


@optendersresource(
    name="aboveThresholdUA:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender cancellations",
)
class TenderUaCancellationResource(BaseTenderCancellationResource):

    @staticmethod
    def cancel_tender_lot_method(request, cancellation):
        return CancelTenderLot()(request, cancellation)

    @json_view(
        content_type="application/json",
        validators=(
            validate_tender_not_in_terminated_status,
            validate_cancellation_data,
            validate_operation_cancellation_in_complaint_period,
            validate_operation_cancellation_permission,
            validate_create_cancellation_in_active_auction,
            validate_cancellation_of_active_lot,
            # from core above ^
            validate_not_only_unsuccessful_awards_or_qualifications,
        ),
        permission="edit_tender"
    )
    def collection_post(self):
        return super(TenderUaCancellationResource, self).collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            validate_tender_not_in_terminated_status,
            validate_operation_cancellation_in_complaint_period,
            validate_cancellation_of_active_lot,
            validate_patch_cancellation_data,
            validate_operation_cancellation_permission,
            validate_cancellation_status_with_complaints,
            # from core above ^,
            validate_not_only_unsuccessful_awards_or_qualifications
        ),
        permission="edit_cancellation"
    )
    def patch(self):
        return super(TenderUaCancellationResource, self).patch()
