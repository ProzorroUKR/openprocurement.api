# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.utils import CancelTenderLot
from openprocurement.tender.core.views.cancellation import BaseTenderCancellationResource

from openprocurement.api.utils import (
    json_view,
    context_unpack,
)
from openprocurement.tender.core.utils import save_tender, apply_patch
from openprocurement.tender.core.validation import (
    validate_tender_not_in_terminated_status,
    validate_cancellation_data,
    validate_patch_cancellation_data,
    validate_cancellation_of_active_lot,
    validate_create_cancellation_in_active_auction,
    validate_cancellation_status_without_complaints,
)


@optendersresource(
    name="belowThreshold:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="belowThreshold",
    description="Tender cancellations",
)
class TenderCancellationResource(BaseTenderCancellationResource):

    @staticmethod
    def cancel_tender_lot_method(request, cancellation):
        return CancelTenderLot()(request, cancellation)

    @json_view(
        content_type="application/json",
        validators=(
            validate_tender_not_in_terminated_status,
            validate_cancellation_data,
            validate_create_cancellation_in_active_auction,
            validate_cancellation_of_active_lot,
        ),
        permission="edit_tender"
    )
    def collection_post(self):
        return super(TenderCancellationResource, self).collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            validate_tender_not_in_terminated_status,
            validate_create_cancellation_in_active_auction,
            validate_patch_cancellation_data,
            validate_cancellation_of_active_lot,
            validate_cancellation_status_without_complaints,
        ),
        permission="edit_cancellation"
    )
    def patch(self):
        cancellation = self.request.context
        prev_status = cancellation.status
        apply_patch(self.request, save=False, src=cancellation.serialize())

        if cancellation.status == "active" and prev_status != "active":
            self.cancel_tender_lot_method(self.request, cancellation)

        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender cancellation {}".format(cancellation.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_cancellation_patch"}),
            )
            return {"data": cancellation.serialize("view")}
