# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.views.cancellation import TenderCancellationResource
from openprocurement.tender.core.validation import (
    validate_tender_not_in_terminated_status,
    validate_cancellation_data,
    validate_patch_cancellation_data,
    validate_cancellation_of_active_lot,
)
from openprocurement.tender.limited.validation import validate_absence_complete_lots_on_tender_cancel


@optendersresource(
    name="reporting:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="reporting",
    description="Tender cancellations",
)
class TenderReportingCancellationResource(TenderCancellationResource):

    def cancel_tender(self):
        tender = self.request.validated["tender"]
        tender.status = "cancelled"

    def cancel_lot(self, cancellation=None):
        raise NotImplementedError("N/A for this procedure")


@optendersresource(
    name="negotiation:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="negotiation",
    description="Tender cancellations",
)
class TenderNegotiationCancellationResource(TenderCancellationResource):
    @json_view(
        content_type="application/json",
        validators=(
            validate_tender_not_in_terminated_status,
            validate_cancellation_data,
            validate_cancellation_of_active_lot,
            # # # from core above ^
            validate_absence_complete_lots_on_tender_cancel,
        ),
        permission="edit_tender"
    )
    def collection_post(self):
        return super(TenderCancellationResource, self).collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            validate_tender_not_in_terminated_status,
            validate_patch_cancellation_data,
            validate_cancellation_of_active_lot,
            # # from core above ^
            validate_absence_complete_lots_on_tender_cancel,
        ),
        permission="edit_tender"
    )
    def patch(self):
        return super(TenderCancellationResource, self).patch()


@optendersresource(
    name="negotiation.quick:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="negotiation.quick",
    description="Tender cancellations",
)
class TenderNegotiationQuickCancellationResource(TenderNegotiationCancellationResource):
    """ Tender Negotiation Quick Cancellation Resource """
