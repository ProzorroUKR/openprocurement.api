# -*- coding: utf-8 -*-
from openprocurement.tender.belowthreshold.views.bid import TenderBidResource
from openprocurement.api.utils import set_ownership, json_view, context_unpack, get_now, raise_operation_error
from openprocurement.tender.core.validation import (
    validate_bid_data,
    validate_patch_bid_data,
    validate_update_deleted_bid,
    validate_bid_operation_period,
    validate_bid_operation_not_in_tendering,
    validate_bid_activate_criteria,
)
from openprocurement.tender.core.utils import save_tender, apply_patch, optendersresource
from openprocurement.tender.openua.validation import validate_update_bid_to_draft, validate_update_bid_to_active_status


@optendersresource(
    name="aboveThresholdUA:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender bids",
)
class TenderUABidResource(TenderBidResource):

    allowed_bid_status_on_create = ["draft", "active"]

    """ """

    @json_view(
        content_type="application/json",
        permission="create_bid",
        validators=(validate_bid_data, validate_bid_operation_not_in_tendering, validate_bid_operation_period),
    )
    def collection_post(self):
        """Registration of new bid proposal

        Creating new Bid proposal
        -------------------------

        Example request to create bid proposal:

        .. sourcecode:: http

            POST /tenders/4879d3f8ee2443169b5fbbc9f89fa607/bids HTTP/1.1
            Host: example.com
            Accept: application/json

            {
                "data": {
                    "tenderers": [
                        {
                            "id": {
                                "name": "Державне управління справами",
                                "scheme": "https://ns.openprocurement.org/ua/edrpou",
                                "uid": "00037256",
                                "uri": "http://www.dus.gov.ua/"
                            },
                            "address": {
                                "countryName": "Україна",
                                "postalCode": "01220",
                                "region": "м. Київ",
                                "locality": "м. Київ",
                                "streetAddress": "вул. Банкова, 11, корпус 1"
                            }
                        }
                    ],
                    "value": {
                        "amount": 489,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    }
                }
            }

        This is what one should expect in response:

        .. sourcecode:: http

            HTTP/1.1 201 Created
            Content-Type: application/json

            {
                "data": {
                    "id": "4879d3f8ee2443169b5fbbc9f89fa607",
                    "status": "registration",
                    "date": "2014-10-28T11:44:17.947Z",
                    "tenderers": [
                        {
                            "id": {
                                "name": "Державне управління справами",
                                "scheme": "https://ns.openprocurement.org/ua/edrpou",
                                "uid": "00037256",
                                "uri": "http://www.dus.gov.ua/"
                            },
                            "address": {
                                "countryName": "Україна",
                                "postalCode": "01220",
                                "region": "м. Київ",
                                "locality": "м. Київ",
                                "streetAddress": "вул. Банкова, 11, корпус 1"
                            }
                        }aaaabid
                    ],
                    "value": {
                        "amount": 489,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    }
                }
            }

        """
        # See https://github.com/open-contracting/standard/issues/78#issuecomment-59830415
        # for more info upon schema
        tender = self.request.validated["tender"]
        bid = self.request.validated["bid"]
        if bid.status not in self.allowed_bid_status_on_create:
            raise_operation_error(
                self.request, "Bid can be added only with status: {}.".format(self.allowed_bid_status_on_create)
            )
        tender.modified = False
        access = set_ownership(bid, self.request)
        tender.bids.append(bid)
        if save_tender(self.request):
            self.LOGGER.info(
                "Created tender bid {}".format(bid.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_bid_create"}, {"bid_id": bid.id}),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tender Bids".format(tender.procurementMethodType), tender_id=tender.id, bid_id=bid["id"]
            )
            return {"data": bid.serialize("view"), "access": access}

    @json_view(
        content_type="application/json",
        permission="edit_bid",
        validators=(
            validate_patch_bid_data,
            validate_bid_operation_not_in_tendering,
            validate_bid_operation_period,
            validate_update_deleted_bid,
            validate_update_bid_to_draft,
            validate_update_bid_to_active_status,
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
                    "activevalue": {
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

        And here is the response to be expected:

        .. sourcecode:: http

            HTTP/1.0 200 OK
            Content-Type: application/json

            {
                "data": {
                    "value": {
                        "amount": 489,
                        "currency": "UAH",
                        "valueAddedTaxIncluded": true
                    }
                }
            }

        """
        bid = self.request.context
        bid.status = "deleted"
        self.request.validated["tender"].modified = False
        if save_tender(self.request):
            res = bid.serialize("view")
            self.LOGGER.info(
                "Deleted tender bid {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_bid_delete"}),
            )
            return {"data": res}
