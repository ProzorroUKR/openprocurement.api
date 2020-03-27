# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view, context_unpack, get_now, raise_operation_error
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.core.utils import save_tender, apply_patch, optendersresource, get_first_revision_date
from openprocurement.tender.core.validation import (
    validate_lot_data,
    validate_patch_lot_data,
    validate_operation_with_lot_cancellation_in_pending,
)
from openprocurement.tender.openua.views.lot import TenderUaLotResource as TenderLotResource
from openprocurement.tender.limited.validation import (
    validate_lot_operation_with_awards,
    validate_lot_operation_not_in_active_status,
)


@optendersresource(
    name="negotiation.quick:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType="negotiation.quick",
    description="Tender limited negotiation quick lots",
)
class TenderLimitedNegotiationQuickLotResource(TenderLotResource):
    route_name = "Tender limited negotiation quick Lots"

    @json_view(
        content_type="application/json",
        validators=(validate_lot_data, validate_lot_operation_not_in_active_status, validate_lot_operation_with_awards),
        permission="edit_tender",
    )
    def collection_post(self):
        """Add a lot
        """
        lot = self.request.validated["lot"]
        lot.date = get_now()
        tender = self.request.validated["tender"]
        tender.lots.append(lot)
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
            validate_operation_with_lot_cancellation_in_pending("lot"),
            validate_lot_operation_not_in_active_status,
            validate_lot_operation_with_awards,
        ),
        permission="edit_tender",
    )
    def patch(self):
        """Update of lot
        """
        tender = self.request.validated["tender"]
        lot = self.request.context
        old_rules = get_first_revision_date(tender, default=get_now()) < RELEASE_2020_04_19

        if old_rules and [
            cancellation for cancellation in tender.get("cancellations") if cancellation.get("relatedLot") == lot["id"]
        ]:
            raise_operation_error(self.request, "Can't update lot that have active cancellation")
        if apply_patch(self.request, src=self.request.context.serialize()):
            self.LOGGER.info(
                "Updated tender lot {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_lot_patch"}),
            )
            return {"data": self.request.context.serialize("view")}

    @json_view(
        permission="edit_tender",
        validators=(
            validate_operation_with_lot_cancellation_in_pending("lot"),
            validate_lot_operation_not_in_active_status,
            validate_lot_operation_with_awards
        ),
    )
    def delete(self):
        """Lot deleting
        """
        lot = self.request.context
        res = lot.serialize("view")
        tender = self.request.validated["tender"]
        tender.lots.remove(lot)
        if save_tender(self.request):
            self.LOGGER.info(
                "Deleted tender lot {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_lot_delete"}),
            )
            return {"data": res}


@optendersresource(
    name="negotiation:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType="negotiation",
    description="Tender limited negotiation lots",
)
class TenderLimitedNegotiationLotResource(TenderLimitedNegotiationQuickLotResource):
    route_name = "Tender limited negotiation Lots"
