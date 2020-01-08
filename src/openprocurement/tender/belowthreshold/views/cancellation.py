# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.utils import add_next_award
from openprocurement.tender.core.views.cancellation import BaseTenderCancellationResource

from openprocurement.api.utils import (
    json_view,
    context_unpack,
)
from openprocurement.tender.core.utils import save_tender, apply_patch
from openprocurement.tender.core.validation import (
    validate_tender_not_in_terminated_status,
    validate_absence_of_pending_accepted_satisfied_complaints,
    validate_patch_cancellation_data,
    validate_cancellation_of_active_lot,
    validate_create_cancellation_in_active_auction,
    validate_cancellation_statuses_without_complaints,
)



@optendersresource(
    name="belowThreshold:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="belowThreshold",
    description="Tender cancellations",
)
class TenderCancellationResource(BaseTenderCancellationResource):
    add_next_award_method = add_next_award

    @json_view(
        content_type="application/json",
        validators=(
                validate_tender_not_in_terminated_status,
                validate_create_cancellation_in_active_auction,
                validate_patch_cancellation_data,
                validate_cancellation_of_active_lot,
                validate_cancellation_statuses_without_complaints,
        ),
        permission="edit_cancellation"
    )
    def patch(self):
        cancellation = self.request.context
        prev_status = cancellation.status
        apply_patch(self.request, save=False, src=cancellation.serialize())

        if cancellation.status == "active":
            if prev_status != "active":
                validate_absence_of_pending_accepted_satisfied_complaints(self.request)
            if cancellation.relatedLot:
                self.cancel_lot(cancellation)
            else:
                self.cancel_tender_method(self.request)

        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender cancellation {}".format(cancellation.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_cancellation_patch"}),
            )
            return {"data": cancellation.serialize("view")}
