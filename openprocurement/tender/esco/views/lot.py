# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.lot import TenderUaLotResource
from openprocurement.tender.openeu.views.lot import TenderEULotResource


@optendersresource(name='Tender ESCO UA Lots',
            collection_path='/tenders/{tender_id}/lots',
            path='/tenders/{tender_id}/lots/{lot_id}',
            procurementMethodType='esco.UA',
            description="Tender ESCO UA lots")
class TenderESCOUALotResource(TenderUaLotResource):
    """ Tender ESCO UA Lot Resource """


@optendersresource(name='Tender ESCO EU Lots',
            collection_path='/tenders/{tender_id}/lots',
            path='/tenders/{tender_id}/lots/{lot_id}',
            procurementMethodType='esco.EU',
            description="Tender ESCO EU lots")
class TenderESCOEULotResource(TenderEULotResource):
    """ Tender ESCO EU Lot Resource """
