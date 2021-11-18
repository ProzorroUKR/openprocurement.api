# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.award import TenderAwardResource as TenderEUAwardResource


# @optendersresource(
#     name="esco:Tender Awards",
#     collection_path="/tenders/{tender_id}/awards",
#     path="/tenders/{tender_id}/awards/{award_id}",
#     description="Tender ESCO Awards",
#     procurementMethodType="esco",
# )
class TenderESCOAwardResource(TenderEUAwardResource):
    """ Tender ESCO Award Resource """
