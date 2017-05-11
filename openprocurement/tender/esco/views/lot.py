# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.lot import TenderEULotResource


@optendersresource(name='Tender ESCO EU Lots',
            collection_path='/tenders/{tender_id}/lots',
            path='/tenders/{tender_id}/lots/{lot_id}',
            procurementMethodType='esco.EU',
            description="Tender ESCO EU lots")
class TenderESCOEULotResource(TenderEULotResource):
    """ Tender ESCO EU Lot Resource """
