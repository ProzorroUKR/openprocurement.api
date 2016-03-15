# -*- coding: utf-8 -*-
from openprocurement.tender.openua.views.bid import TenderUABidResource as TenderBidResource
from openprocurement.api.utils import opresource


@opresource(name='Tender UA.defense Bids',
            collection_path='/tenders/{tender_id}/bids',
            path='/tenders/{tender_id}/bids/{bid_id}',
            procurementMethodType='aboveThresholdUA.defense',
            description="Tender UA.defense bids")
class TenderUABidResource(TenderBidResource):
    """ """
