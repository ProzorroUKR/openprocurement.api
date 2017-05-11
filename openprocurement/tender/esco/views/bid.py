# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource

from openprocurement.tender.openeu.views.bid import TenderBidResource as TenderEUBidResource


@optendersresource(name='Tender ESCO EU Bids',
            collection_path='/tenders/{tender_id}/bids',
            path='/tenders/{tender_id}/bids/{bid_id}',
            procurementMethodType='esco.EU',
            description="Tender ESCO EU bids")
class TenderESCOEUBidResource(TenderEUBidResource):
    """ Tender ESCO EU Bid Resource """
