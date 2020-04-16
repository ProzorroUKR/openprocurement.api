# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.cancellation import BaseTenderCancellationResource
from openprocurement.tender.belowthreshold.views.cancellation import \
    TenderCancellationResource as BaseTenderReportingCancellationResource
from openprocurement.tender.core.validation import (
    validate_tender_not_in_terminated_status,
    validate_cancellation_data,
    validate_patch_cancellation_data,
    validate_cancellation_of_active_lot,
    validate_create_cancellation_in_active_auction,
    validate_operation_cancellation_in_complaint_period,
    validate_operation_cancellation_permission,
)
from openprocurement.tender.limited.validation import (
    validate_absence_complete_lots_on_tender_cancel,
    validate_cancellation_status,
)
from openprocurement.tender.limited.utils import ReportingCancelTenderLot


@optendersresource(
    name="reporting:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="reporting",
    description="Tender cancellations",
)
class TenderReportingCancellationResource(BaseTenderReportingCancellationResource):

    @staticmethod
    def cancel_tender_lot_method(request, cancellation):
        return ReportingCancelTenderLot()(request, cancellation)



@optendersresource(
    name="negotiation:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="negotiation",
    description="Tender cancellations",
)
class TenderNegotiationCancellationResource(BaseTenderCancellationResource):
    @json_view(
        content_type="application/json",
        validators=(
            validate_tender_not_in_terminated_status,
            validate_cancellation_data,
            validate_operation_cancellation_permission,
            validate_operation_cancellation_in_complaint_period,
            validate_create_cancellation_in_active_auction,
            validate_cancellation_of_active_lot,
            # # # from core above ^
            validate_absence_complete_lots_on_tender_cancel,
        ),
        permission="edit_tender"
    )
    def collection_post(self):
        return super(TenderNegotiationCancellationResource, self).collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            validate_tender_not_in_terminated_status,
            validate_patch_cancellation_data,
            validate_operation_cancellation_permission,
            validate_operation_cancellation_in_complaint_period,
            validate_cancellation_status,
            validate_cancellation_of_active_lot,
            # # from core above ^
            validate_absence_complete_lots_on_tender_cancel,
        ),
        permission="edit_cancellation"
    )
    def patch(self):
        return super(TenderNegotiationCancellationResource, self).patch()


@optendersresource(
    name="negotiation.quick:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="negotiation.quick",
    description="Tender cancellations",
)
class TenderNegotiationQuickCancellationResource(TenderNegotiationCancellationResource):
    """ Tender Negotiation Quick Cancellation Resource """
