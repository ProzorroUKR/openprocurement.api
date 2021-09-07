# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view, context_unpack
from openprocurement.tender.core.validation import validate_tender_auction_data
from openprocurement.tender.core.utils import apply_patch, save_tender, optendersresource
from openprocurement.tender.openua.views.auction import TenderUaAuctionResource as BaseResource
from openprocurement.tender.cfaua.utils import add_next_awards


# @optendersresource(
#     name="closeFrameworkAgreementUA:Tender Auction",
#     collection_path="/tenders/{tender_id}/auction",
#     path="/tenders/{tender_id}/auction/{auction_lot_id}",
#     procurementMethodType="closeFrameworkAgreementUA",
#     description="Tender EU auction data",
# )
class TenderAuctionResource(BaseResource):
    """ Auctions resouce """

    @json_view(content_type="application/json", permission="auction", validators=(validate_tender_auction_data))
    def collection_post(self):
        """Report auction results.

        Report auction results
        ----------------------

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
            add_next_awards(
                self.request,
                reverse=configurator.reverse_awarding_criteria,
                awarding_criteria_key=configurator.awarding_criteria_key,
            )
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
            add_next_awards(
                self.request,
                reverse=configurator.reverse_awarding_criteria,
                awarding_criteria_key=configurator.awarding_criteria_key,
            )
        if save_tender(self.request):
            self.LOGGER.info(
                "Report auction results", extra=context_unpack(self.request, {"MESSAGE_ID": "tender_lot_auction_post"})
            )
            return {"data": self.request.validated["tender"].serialize(self.request.validated["tender"].status)}
