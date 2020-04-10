# -*- coding: utf-8 -*-
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.utils import json_view, get_now, get_first_revision_date, context_unpack
from openprocurement.tender.core.utils import optendersresource, save_tender, apply_patch
from openprocurement.tender.belowthreshold.views.cancellation import\
    TenderCancellationResource
from openprocurement.tender.core.validation import validate_tender_not_in_terminated_status, validate_cancellation_data, \
    validate_cancellation_of_active_lot, validate_absence_of_pending_accepted_satisfied_complaints, \
    validate_patch_cancellation_data, validate_cancellation_statuses_without_complaints
from openprocurement.tender.pricequotation.constants import PMT
from openprocurement.tender.pricequotation.validation import validate_create_cancellation_in_active_auction


@optendersresource(
    name="{}:Tender Cancellations".format(PMT),
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType=PMT,
    description="Tender cancellations",
)
class PQTenderCancellationResource(TenderCancellationResource):
    """PriceQuotation cancellation"""

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
        cancellation = self.request.validated["cancellation"]
        cancellation.date = get_now()

        if get_first_revision_date(self.request.tender, default=get_now()) > RELEASE_2020_04_19 \
                and cancellation.cancellationOf == "tender":
            cancellation.status = None

        if cancellation.status == "active":
            validate_absence_of_pending_accepted_satisfied_complaints(self.request)
            self.cancel_tender_method(self.request)

        self.request.context.cancellations.append(cancellation)
        if save_tender(self.request):
            self.LOGGER.info(
                "Created tender cancellation {}".format(cancellation.id),
                extra=context_unpack(
                    self.request, {"MESSAGE_ID": "tender_cancellation_create"}, {"cancellation_id": cancellation.id}
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tender Cancellations".format(self.request.validated["tender"].procurementMethodType),
                tender_id=self.request.validated["tender_id"],
                cancellation_id=cancellation.id,
            )
            return {"data": cancellation.serialize("view")}

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
            self.cancel_tender_method(self.request)

        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender cancellation {}".format(cancellation.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_cancellation_patch"}),
            )
            return {"data": cancellation.serialize("view")}
