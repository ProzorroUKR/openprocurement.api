# -*- coding: utf-8 -*-
from datetime import timedelta

from openprocurement.api.utils import (
    json_view,
    context_unpack,
    APIResource,
    get_now,
    get_first_revision_date,
)
from openprocurement.tender.core.utils import calculate_complaint_business_date
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.core.utils import save_tender, apply_patch, cancel_tender
from openprocurement.tender.core.validation import (
    validate_tender_not_in_terminated_status,
    validate_absence_of_pending_accepted_satisfied_complaints,
    validate_cancellation_data,
    validate_patch_cancellation_data,
    validate_cancellation_of_active_lot,
    validate_cancellation_statuses,
    validate_edit_permission,
    validate_create_cancellation_in_active_auction,
)


class BaseTenderCancellationResource(APIResource):

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
            if cancellation.relatedLot:
                self.cancel_lot(cancellation)
            else:
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

    @json_view(permission="view_tender")
    def collection_get(self):
        return {"data": [i.serialize("view") for i in self.request.validated["tender"].cancellations]}

    @json_view(permission="view_tender")
    def get(self):
        return {"data": self.request.validated["cancellation"].serialize("view")}

    @json_view(
        content_type="application/json",
        validators=(
            validate_edit_permission,
            validate_tender_not_in_terminated_status,
            validate_patch_cancellation_data,
            validate_cancellation_statuses,
            validate_cancellation_of_active_lot,
        ),
        permission="edit_cancellation"
    )
    def patch(self):
        cancellation = self.request.context
        prev_status = cancellation.status
        apply_patch(self.request, save=False, src=cancellation.serialize())

        if get_first_revision_date(self.request.tender, default=get_now()) > RELEASE_2020_04_19 \
                and cancellation.cancellationOf == "tender":

            if prev_status == "draft" and cancellation.status == "pending":
                tender = self.request.validated["tender"]
                now = get_now()
                cancellation.complaintPeriod = {
                    "startDate": now.isoformat(),
                    "endDate": calculate_complaint_business_date(
                        now, timedelta(days=10), tender).isoformat()
                }

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

    # methods below are used by views and can be redefined at child models
    @staticmethod
    def add_next_award_method(request):
        raise NotImplementedError

    @staticmethod
    def cancel_tender_method(request):
        return cancel_tender(request)

    def cancel_lot(self, cancellation):
        tender = self.request.validated["tender"]
        self._cancel_lots(tender, cancellation)
        self._lot_update_check_tender_status(tender)

        if tender.status == "active.auction" and all(
            i.auctionPeriod and i.auctionPeriod.endDate
            for i in self.request.validated["tender"].lots
            if i.numberOfBids > 1 and i.status == "active"
        ):
            self.add_next_award_method(self.request)

    # methods below are used by methods above
    def _lot_update_check_tender_status(self, tender):
        lot_statuses = {lot.status for lot in tender.lots}
        if lot_statuses == {"cancelled"}:
            self.cancel_tender_method(self.request)
        elif not lot_statuses.difference({"unsuccessful", "cancelled"}):
            tender.status = "unsuccessful"
        elif not lot_statuses.difference({"complete", "unsuccessful", "cancelled"}):
            tender.status = "complete"

    @staticmethod
    def _cancel_lots(tender, cancellation):
        for lot in tender.lots:
            if lot.id == cancellation.relatedLot:
                lot.status = "cancelled"
