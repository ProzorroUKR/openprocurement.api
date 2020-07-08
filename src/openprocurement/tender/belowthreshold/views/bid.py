# -*- coding: utf-8 -*-
from openprocurement.api.utils import get_now, set_ownership, json_view, context_unpack, APIResource

from openprocurement.tender.core.validation import (
    validate_bid_data,
    validate_patch_bid_data,
    validate_bid_operation_period,
    validate_bid_operation_not_in_tendering,
)

from openprocurement.tender.belowthreshold.validation import validate_view_bids, validate_update_bid_status

from openprocurement.tender.core.utils import save_tender, optendersresource, apply_patch


@optendersresource(
    name="belowThreshold:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType="belowThreshold",
    description="Tender bids",
)
class TenderBidResource(APIResource):
    @json_view(
        content_type="application/json",
        permission="create_bid",
        validators=(
            validate_bid_operation_not_in_tendering,
            validate_bid_data,
            validate_bid_operation_period
        ),
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
                        }
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
        access = set_ownership(bid, self.request)
        tender.bids.append(bid)
        tender.modified = False
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

    @json_view(permission="view_tender", validators=(validate_view_bids,))
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
        validate_view_bids(self.request)
        return {"data": self.request.context.serialize(self.request.validated["tender_status"])}

    @json_view(
        content_type="application/json",
        permission="edit_bid",
        validators=(
            validate_patch_bid_data,
            validate_bid_operation_not_in_tendering,
            validate_bid_operation_period,
            validate_update_bid_status,
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
        res = bid.serialize("view")
        self.request.validated["tender"].bids.remove(bid)
        self.request.validated["tender"].modified = False
        if save_tender(self.request):
            self.LOGGER.info(
                "Deleted tender bid {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_bid_delete"}),
            )
            return {"data": res}
