# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.bid import (
    TenderUABidResource as TenderBidResource
)


@optendersresource(name='aboveThresholdUA.defense:Tender Bids',
                   collection_path='/tenders/{tender_id}/bids',
                   path='/tenders/{tender_id}/bids/{bid_id}',
                   procurementMethodType='aboveThresholdUA.defense',
                   description="Tender UA.defense bids")
class TenderUABidResource(TenderBidResource):
    """ """
