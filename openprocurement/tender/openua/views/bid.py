# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.utils import opresource, json_view, save_tender, context_unpack
from openprocurement.api.views.bid import TenderBidResource
from openprocurement.tender.openua.views.tender import isTenderUA


LOGGER = getLogger(__name__)


@opresource(name='Tender UA Bids',
            collection_path='/tenders/{tender_id}/bids',
            path='/tenders/{tender_id}/bids/{bid_id}',
            custom_predicates=(isTenderUA,),
            description="Tender bids")
class TenderUABidResource(TenderBidResource):
    """ """

    @json_view(permission='edit_bid')
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
        if self.request.validated['tender_status'] != 'active.tendering':
            self.request.errors.add('body', 'data', 'Can\'t delete bid in current ({}) tender status'.format(self.request.validated['tender_status']))
            self.request.errors.status = 403
            return
        res = bid.serialize("view")
        self.request.validated['tender'].bids.remove(bid)
        if save_tender(self.request):
            LOGGER.info('Deleted tender bid {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_bid_delete'}))
            return {'data': res}
