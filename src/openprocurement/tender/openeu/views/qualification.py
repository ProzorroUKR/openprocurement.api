# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view, context_unpack, APIResource, raise_operation_error
from openprocurement.tender.core.utils import save_tender, apply_patch
from openprocurement.tender.core.validation import validate_operation_with_lot_cancellation_in_pending
from openprocurement.tender.openeu.validation import (
    validate_patch_qualification_data,
    validate_cancelled_qualification_update,
    validate_qualification_update_not_in_pre_qualification,
)
from openprocurement.tender.openeu.utils import qualifications_resource, prepare_qualifications


@qualifications_resource(
    name="aboveThresholdEU:Tender Qualification",
    collection_path="/tenders/{tender_id}/qualifications",
    path="/tenders/{tender_id}/qualifications/{qualification_id}",
    procurementMethodType="aboveThresholdEU",
    description="TenderEU Qualification",
)
class TenderQualificationResource(APIResource):
    @json_view(permission="view_tender")
    def collection_get(self):
        """List qualifications
        """
        return {"data": [i.serialize("view") for i in self.request.validated["tender"].qualifications]}

    @json_view(permission="view_tender")
    def get(self):
        """Retrieving the qualification
        """
        return {"data": self.request.validated["qualification"].serialize("view")}

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_qualification_data,
            validate_operation_with_lot_cancellation_in_pending("qualification"),
            validate_qualification_update_not_in_pre_qualification,
            validate_cancelled_qualification_update,
        ),
        permission="edit_tender",
    )
    def patch(self):
        """Post a qualification resolution
        """

        def set_bid_status(tender, bid_id, status, lotId=None):
            if lotId:
                for bid in tender.bids:
                    if bid.id == bid_id:
                        for lotValue in bid.lotValues:
                            if lotValue.relatedLot == lotId:
                                lotValue.status = status
                                if status in ["pending", "active"]:
                                    bid.status = status
                                return bid
            for bid in tender.bids:
                if bid.id == bid_id:
                    bid.status = status
                    return bid

        tender = self.request.validated["tender"]
        prev_status = self.request.context.status
        apply_patch(self.request, save=False, src=self.request.context.serialize())
        if prev_status != "pending" and self.request.context.status != "cancelled":
            raise_operation_error(self.request, "Can't update qualification status".format(tender.status))
        if self.request.context.status == "active":
            # approve related bid
            set_bid_status(tender, self.request.context.bidID, "active", self.request.context.lotID)
        elif self.request.context.status == "unsuccessful":
            # cancel related bid
            set_bid_status(tender, self.request.context.bidID, "unsuccessful", self.request.context.lotID)
        elif self.request.context.status == "cancelled":
            # return bid to initial status
            bid = set_bid_status(tender, self.request.context.bidID, "pending", self.request.context.lotID)
            # generate new qualification for related bid
            ids = prepare_qualifications(self.request, bids=[bid], lotId=self.request.context.lotID)
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tender Qualification".format(tender.procurementMethodType),
                tender_id=tender.id,
                qualification_id=ids[0],
            )
        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender qualification {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_qualification_patch"}),
            )
            return {"data": self.request.context.serialize("view")}
