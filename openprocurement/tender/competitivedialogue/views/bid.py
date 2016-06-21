# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openeu.views.bid import TenderBidResource as BaseResourceEU
from openprocurement.tender.competitivedialogue.models import CD_EU_TYPE, CD_UA_TYPE


@opresource(name='Competitive Dialogue EU Bids',
            collection_path='/tenders/{tender_id}/bids',
            path='/tenders/{tender_id}/bids/{bid_id}',
            procurementMethodType=CD_EU_TYPE,
            description="Competitive Dialogue EU bids")
class CompetitiveDialogueEUBidResource(BaseResourceEU):
    """ Tender EU bids """
    pass


@opresource(name='Competitive Dialogue UA Bids',
            collection_path='/tenders/{tender_id}/bids',
            path='/tenders/{tender_id}/bids/{bid_id}',
            procurementMethodType=CD_UA_TYPE,
            description="Competitive Dialogue UA bids")
class CompetitiveDialogueUABidResource(BaseResourceEU):
    """ Tender UA bids """
    pass
