# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openuadefense.views.award import TenderUaAwardResource


# @optendersresource(
#     name="simple.defense:Tender Awards",
#     collection_path="/tenders/{tender_id}/awards",
#     path="/tenders/{tender_id}/awards/{award_id}",
#     description="Tender awards",
#     procurementMethodType="simple.defense",
# )
class TenderSimpleDefResource(TenderUaAwardResource):
    """"""
