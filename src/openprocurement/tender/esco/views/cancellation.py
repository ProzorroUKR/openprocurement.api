# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.cancellation import TenderCancellationResource as TenderEUCancellationResource


# @optendersresource(
#     name="esco:Tender Cancellations",
#     collection_path="/tenders/{tender_id}/cancellations",
#     path="/tenders/{tender_id}/cancellations/{cancellation_id}",
#     procurementMethodType="esco",
#     description="Tender ESCO Cancellations",
# )
class TenderESCOCancellationResource(TenderEUCancellationResource):
    """ Tender ESCO Cancellation Resource """
