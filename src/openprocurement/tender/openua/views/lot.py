# -*- coding: utf-8 -*-
from openprocurement.tender.belowthreshold.views.lot import TenderLotResource
from openprocurement.api.utils import get_now, json_view, context_unpack
from openprocurement.tender.core.validation import (
    validate_lot_data,
    validate_patch_lot_data,
    validate_tender_period_extension,
    validate_lot_operation_not_in_allowed_status,
    validate_operation_with_lot_cancellation_in_pending,
)
from openprocurement.tender.core.utils import (
    save_tender,
    apply_patch,
    optendersresource,
)


@optendersresource(
    name="aboveThresholdUA:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender Ua lots",
)
class TenderUaLotResource(TenderLotResource):
    @json_view(
        content_type="application/json",
        validators=(
            validate_lot_data,
            validate_lot_operation_not_in_allowed_status,
            validate_tender_period_extension,
        ),
        permission="edit_tender",
    )
    def collection_post(self):
        """Add a lot
        """
        lot = self.request.validated["lot"]
        lot.date = get_now()
        tender = self.request.validated["tender"]
        tender.lots.append(lot)
        if self.request.authenticated_role == "tender_owner":
            tender.invalidate_bids_data()
        if save_tender(self.request):
            self.LOGGER.info(
                "Created tender lot {}".format(lot.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_lot_create"}, {"lot_id": lot.id}),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tender Lots".format(tender.procurementMethodType), tender_id=tender.id, lot_id=lot.id
            )
            return {"data": lot.serialize("view")}

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_lot_data,
            validate_lot_operation_not_in_allowed_status,
            validate_operation_with_lot_cancellation_in_pending("lot"),
            validate_tender_period_extension,
        ),
        permission="edit_tender",
    )
    def patch(self):
        """Update of lot
        """
        if self.request.authenticated_role == "tender_owner":
            self.request.validated["tender"].invalidate_bids_data()
        if apply_patch(self.request, src=self.request.context.serialize()):
            self.LOGGER.info(
                "Updated tender lot {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_lot_patch"}),
            )
            return {"data": self.request.context.serialize("view")}

    @json_view(
        permission="edit_tender",
        validators=(
            validate_lot_operation_not_in_allowed_status,
            validate_operation_with_lot_cancellation_in_pending("lot"),
            validate_tender_period_extension,
        ),
    )
    def delete(self):
        """Lot deleting
        """
        lot = self.request.context
        res = lot.serialize("view")
        tender = self.request.validated["tender"]
        tender.lots.remove(lot)
        if self.request.authenticated_role == "tender_owner":
            tender.invalidate_bids_data()
        if save_tender(self.request):
            self.LOGGER.info(
                "Deleted tender lot {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_lot_delete"}),
            )
            return {"data": res}
