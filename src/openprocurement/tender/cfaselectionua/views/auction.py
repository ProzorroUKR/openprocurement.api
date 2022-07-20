# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view, context_unpack
from openprocurement.tender.core.validation import validate_tender_auction_data
from openprocurement.tender.core.utils import (
    save_tender,
    optendersresource,
    apply_patch,
)

from openprocurement.tender.belowthreshold.utils import add_next_award
from openprocurement.tender.cfaselectionua.validation import validate_auction_info_view


# @optendersresource(
#     name="closeFrameworkAgreementSelectionUA:Tender Auction",
#     collection_path="/tenders/{tender_id}/auction",
#     path="/tenders/{tender_id}/auction/{auction_lot_id}",
#     procurementMethodType="closeFrameworkAgreementSelectionUA",
#     description="Tender auction data",
# )
class TenderAuctionResource:
    @json_view(permission="auction", validators=(validate_auction_info_view))
    def collection_get(self):
        """Get auction info.

        Get tender auction info
        -----------------------

        Example request to get tender auction information:

        .. sourcecode:: http

            GET /tenders/4879d3f8ee2443169b5fbbc9f89fa607/auction HTTP/1.1
            Host: example.com
            Accept: application/json

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
                                "amount": 500,
                                "currency": "UAH",
                                "valueAddedTaxIncluded": true
                            }
                        },
                        {
                            "value": {
                                "amount": 485,
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
        return {"data": self.request.validated["tender"].serialize("auction_view")}

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
                if i.numberOfBids > 1 and i.status == "active"
            ]
        ):
            add_next_award(self.request)
        if save_tender(self.request):
            self.LOGGER.info(
                "Report auction results", extra=context_unpack(self.request, {"MESSAGE_ID": "tender_lot_auction_post"})
            )
            return {"data": self.request.validated["tender"].serialize(self.request.validated["tender"].status)}
