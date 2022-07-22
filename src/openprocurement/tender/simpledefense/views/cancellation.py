# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.cancellation import TenderUaCancellationResource as TenderCancellationResource


# @optendersresource(
#     name="simple.defense:Tender Cancellations",
#     collection_path="/tenders/{tender_id}/cancellations",
#     path="/tenders/{tender_id}/cancellations/{cancellation_id}",
#     procurementMethodType="simple.defense",
#     description="Tender cancellations",
# )
class TenderUaCancellationResource(TenderCancellationResource):
    pass
