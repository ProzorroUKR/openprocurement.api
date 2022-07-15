# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.lot import TenderEULotResource


# @optendersresource(
#     name="esco:Tender Lots",
#     collection_path="/tenders/{tender_id}/lots",
#     path="/tenders/{tender_id}/lots/{lot_id}",
#     procurementMethodType="esco",
#     description="Tender ESCO lots",
# )
class TenderESCOLotResource(TenderEULotResource):
    """ Tender ESCO Lot Resource """
