# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view, context_unpack, get_now
from openprocurement.tender.core.utils import optendersresource, apply_patch, save_tender
from openprocurement.tender.core.validation import (
    validate_patch_bid_data,
    validate_update_deleted_bid,
    validate_bid_operation_period,
    validate_bid_operation_not_in_tendering,
    validate_bid_status_update_not_to_pending,
    validate_bid_activate_criteria,
)
from openprocurement.tender.openua.views.bid import TenderUABidResource as BaseResource
from openprocurement.tender.cfaua.validation import validate_view_bids_in_active_tendering


@optendersresource(
    name="closeFrameworkAgreementUA:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender EU bids",
)
class TenderBidResource(BaseResource):

    allowed_bid_status_on_create = ["draft", "pending"]

    """ Tender EU bids """

    @json_view(permission="view_tender", validators=(validate_view_bids_in_active_tendering))
    def collection_get(self):
        """Bids Listing

        Get Bids List
        -------------

        Example request to get bids list:

        .. sourcecode:: http

            GET /tenders/4879d3f8ee2443169b5fbbc9f89fa607/bids HTTP/1.1
            Host: example.com
            Accept: application/json

        This is what one should expect in response:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "data": [
                    {
                        "value": {
                            "amount": 489,
                            "currency": "UAH",
                            "valueAddedTaxIncluded": true
                        }
                    }
                ]
            }

        """
        tender = self.request.validated["tender"]
        return {"data": [i.serialize(self.request.validated["tender_status"]) for i in tender.bids]}

    @json_view(permission="view_tender")
    def get(self):
        """Retrieving the proposal

        Example request for retrieving the proposal:

        .. sourcecode:: http

            GET /tenders/4879d3f8ee2443169b5fbbc9f89fa607/bids/71b6c23ed8944d688e92a31ec8c3f61a HTTP/1.1
            Host: example.com
            Accept: application/json

        And here is the response to be expected:

        .. sourcecode:: http

            HTTP/1.0 200 OK
            Content-Type: application/json

            {
                "data": {
                    "value": {
                        "amount": 600,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    }
                }
            }

        """
        if self.request.authenticated_role == "bid_owner":
            return {"data": self.request.context.serialize("view")}
        # TODO can't move this validator becacuse of check above
        validate_view_bids_in_active_tendering(self.request)
        return {"data": self.request.context.serialize(self.request.validated["tender_status"])}

    @json_view(
        content_type="application/json",
        permission="edit_bid",
        validators=(
            validate_patch_bid_data,
            validate_bid_operation_not_in_tendering,
            validate_bid_operation_period,
            validate_update_deleted_bid,
            validate_bid_status_update_not_to_pending,
            validate_bid_activate_criteria,
        ),
    )
    def patch(self):
        """Update of proposal

        Example request to change bid proposal:

        .. sourcecode:: http

            PATCH /tenders/4879d3f8ee2443169b5fbbc9f89fa607/bids/71b6c23ed8944d688e92a31ec8c3f61a HTTP/1.1
            Host: example.com
            Accept: application/json

            {
                "data": {
                    "value": {
                        "amount": 600
                    }
                }
            }

        And here is the response to be expected:

        .. sourcecode:: http

            HTTP/1.0 200 OK
            Content-Type: application/json

            {
                "data": {
                    "value": {
                        "amount": 600,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    }
                }
            }

        """
        value = self.request.validated["data"].get("value") and self.request.validated["data"]["value"].get("amount")
        if value and value != self.request.context.get("value", {}).get("amount"):
            self.request.validated["data"]["date"] = get_now().isoformat()
        if self.request.context.lotValues:
            lotValues = dict([(i.relatedLot, i.value.amount) for i in self.request.context.lotValues])
            for lotvalue in self.request.validated["data"].get("lotValues", []):
                if (
                    lotvalue["relatedLot"] in lotValues
                    and lotvalue.get("value", {}).get("amount") != lotValues[lotvalue["relatedLot"]]
                ):
                    lotvalue["date"] = get_now().isoformat()
        self.request.validated["tender"].modified = False
        if apply_patch(self.request, src=self.request.context.serialize()):
            self.LOGGER.info(
                "Updated tender bid {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_bid_patch"}),
            )
            return {"data": self.request.context.serialize("view")}

    @json_view(
        permission="edit_bid", validators=(validate_bid_operation_not_in_tendering, validate_bid_operation_period)
    )
    def delete(self):
        """Cancelling the proposal

        Example request for cancelling the proposal:

        .. sourcecode:: http

            DELETE /tenders/4879d3f8ee2443169b5fbbc9f89fa607/bids/71b6c23ed8944d688e92a31ec8c3f61a HTTP/1.1
            Host: example.com
            Accept: application/json

        """
        bid = self.request.context
        tender = self.request.validated["tender"]
        bid.status = "deleted"
        if tender.lots:
            bid.lotValues = []
        self.request.validated["tender"].modified = False
        if save_tender(self.request):
            res = bid.serialize("view")
            self.LOGGER.info(
                "Deleted tender bid {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_bid_delete"}),
            )
            return {"data": res}
