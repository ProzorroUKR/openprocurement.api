# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.utils import opresource
from openprocurement.api.views.bid import TenderBidResource as BaseResource


LOGGER = getLogger(__name__)


@opresource(name='Tender EU Bids',
            collection_path='/tenders/{tender_id}/bids',
            path='/tenders/{tender_id}/bids/{bid_id}',
            procurementMethodType='aboveThresholdEU',
            description="Tender EU bids")
class TenderBidResource(BaseResource):
    """ Tender EU bids """
