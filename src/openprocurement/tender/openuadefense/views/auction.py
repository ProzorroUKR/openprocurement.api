# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
    context_unpack,
)
from openprocurement.tender.core.utils import (
    apply_patch,
    save_tender,
    optendersresource
)

from openprocurement.tender.core.validation import (
    validate_tender_auction_data,
)
from openprocurement.tender.belowthreshold.views.auction import (
    TenderAuctionResource
)
from openprocurement.tender.openua.utils import add_next_award


@optendersresource(name='aboveThresholdUA.defense:Auction',
                   collection_path='/tenders/{tender_id}/auction',
                   path='/tenders/{tender_id}/auction/{auction_lot_id}',
                   procurementMethodType='aboveThresholdUA.defense',
                   description="Tender UA.defense auction data")
class TenderUaAuctionResource(TenderAuctionResource):
    """ """
    @json_view(content_type="application/json", permission='auction', validators=(validate_tender_auction_data))
    def collection_post(self):
        """Report auction results.
        """
        apply_patch(self.request, save=False, src=self.request.validated['tender_src'])
        if all([i.auctionPeriod and i.auctionPeriod.endDate for i in self.request.validated['tender'].lots if i.numberOfBids > 1 and i.status == 'active']):
            add_next_award(self.request)
        if save_tender(self.request):
            self.LOGGER.info('Report auction results', extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_auction_post'}))
            return {'data': self.request.validated['tender'].serialize(self.request.validated['tender'].status)}

    @json_view(content_type="application/json", permission='auction', validators=(validate_tender_auction_data))
    def post(self):
        """Report auction results for lot.
        """
        apply_patch(self.request, save=False, src=self.request.validated['tender_src'])
        if all([i.auctionPeriod and i.auctionPeriod.endDate for i in self.request.validated['tender'].lots if i.numberOfBids > 1 and i.status == 'active']):
            add_next_award(self.request)
        if save_tender(self.request):
            self.LOGGER.info('Report auction results', extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_lot_auction_post'}))
            return {'data': self.request.validated['tender'].serialize(self.request.validated['tender'].status)}
