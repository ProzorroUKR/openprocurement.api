# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view, context_unpack
from openprocurement.tender.core.validation import validate_tender_auction_data
from openprocurement.tender.core.utils import apply_patch, save_tender, optendersresource
from openprocurement.tender.belowthreshold.views.auction import TenderAuctionResource
from openprocurement.tender.belowthreshold.utils import add_next_award


# @optendersresource(
#     name="aboveThresholdUA:Tender Auction",
#     collection_path="/tenders/{tender_id}/auction",
#     path="/tenders/{tender_id}/auction/{auction_lot_id}",
#     procurementMethodType="aboveThresholdUA",
#     description="Tender UA auction data",
# )
class TenderUaAuctionResource(TenderAuctionResource):
    @json_view(content_type="application/json", permission="auction", validators=(validate_tender_auction_data))
    def collection_post(self):
        """Report auction results.

        Report auction results
        ----------------------

        Example request to report auction results:

        .. sourcecode:: http

            POST /tenders/4879d3f8ee2443169b5fbbc9f89fa607/auction HTTP/1.1
            Host: example.com
            Accept: application/json

            {
                "data": {
                    "dateModified": "2014-10-27T08:06:58.158Z",
                    "bids": [
                        {
                            "value": {
                                "amount": 400,
                                "currency": "UAH"
                            }
                        },
                        {
                            "value": {
                                "amount": 385,
                                "currency": "UAH"
                            }
                        }
                    ]
                }
            }

        This is what one should expect in response:

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "data": {
                    "dateModified": "2014-10-27T08:06:58.158Z",
                    "bids": [
                        {
                            "value": {
                                "amount": 400,
                                "currency": "UAH",
                                "valueAddedTaxIncluded": true
                            }
                        },
                        {
                            "value": {
                                "amount": 385,
                                "currency": "UAH",
                                "valueAddedTaxIncluded": true
                            }
                        }
                    ],
                    "minimalStep":{
                        "amount": 35,
                        "currency": "UAH"
                    },
                    "tenderPeriod":{
                        "startDate": "2014-11-04T08:00:00"
                    }
                }
            }

        """
        apply_patch(self.request, save=False, src=self.request.validated["tender_src"])
        if all(
            [
                i.auctionPeriod and i.auctionPeriod.endDate
                for i in self.request.validated["tender"].lots
                if i.status == "active"
            ]
        ):
            add_next_award(self.request)
        if save_tender(self.request):
            self.LOGGER.info(
                "Report auction results", extra=context_unpack(self.request, {"MESSAGE_ID": "tender_auction_post"})
            )
            return {"data": self.request.validated["tender"].serialize(self.request.validated["tender"].status)}

    @json_view(content_type="application/json", permission="auction", validators=(validate_tender_auction_data))
    def patch(self):
        """Set urls for access to auction for lot.
        """
        if apply_patch(self.request, src=self.request.validated["tender_src"]):
            self.LOGGER.info(
                "Updated auction urls", extra=context_unpack(self.request, {"MESSAGE_ID": "tender_lot_auction_patch"})
            )
            return {"data": self.request.validated["tender"].serialize("auction_view")}

    @json_view(content_type="application/json", permission="auction", validators=(validate_tender_auction_data))
    def post(self):
        """Report auction results for lot.
        """
        apply_patch(self.request, save=False, src=self.request.validated["tender_src"])
        if all(
            [
                i.auctionPeriod and i.auctionPeriod.endDate
                for i in self.request.validated["tender"].lots
                if i.status == "active"
            ]
        ):
            configurator = self.request.content_configurator
            add_next_award(self.request)
        if save_tender(self.request):
            self.LOGGER.info(
                "Report auction results", extra=context_unpack(self.request, {"MESSAGE_ID": "tender_lot_auction_post"})
            )
            return {"data": self.request.validated["tender"].serialize(self.request.validated["tender"].status)}
