# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.lot import TenderUaLotResource
from openprocurement.tender.openeu.views.lot import TenderEULotResource


@opresource(name='Tender ESCO UA Lots',
            collection_path='/tenders/{tender_id}/lots',
            path='/tenders/{tender_id}/lots/{lot_id}',
            procurementMethodType='esco.UA',
            description="Tender ESCO UA lots")
class TenderESCOUALotResource(TenderUaLotResource):
    """ Tender ESCO UA Lot Resource """


@opresource(name='Tender ESCO EU Lots',
            collection_path='/tenders/{tender_id}/lots',
            path='/tenders/{tender_id}/lots/{lot_id}',
            procurementMethodType='esco.EU',
            description="Tender ESCO EU lots")
class TenderESCOEULotResource(TenderEULotResource):
    """ Tender ESCO EU Lot Resource """
