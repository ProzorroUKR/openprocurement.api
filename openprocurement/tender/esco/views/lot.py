# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openeu.views.lot import TenderEULotResource


@opresource(name='Tender ESCO EU Lots',
            collection_path='/tenders/{tender_id}/lots',
            path='/tenders/{tender_id}/lots/{lot_id}',
            procurementMethodType='esco.EU',
            description="Tender ESCO EU lots")
class TenderESCOEULotResource(TenderEULotResource):
    """ Tender ESCO EU Lot Resource """
