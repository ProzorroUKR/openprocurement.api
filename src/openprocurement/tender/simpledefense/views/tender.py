# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openuadefense.views.tender import TenderUAResource


# @optendersresource(
#     name="simple.defense:Tender",
#     path="/tenders/{tender_id}",
#     procurementMethodType="simple.defense",
#     description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info",
# )
class TenderSimpleDefResource(TenderUAResource):
    """ Resource handler for TenderUA """

