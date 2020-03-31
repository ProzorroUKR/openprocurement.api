# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource

from openprocurement.tender.belowthreshold.views.complaint import\
    TenderComplaintResource as BaseTenderComplaintResource
from openprocurement.tender.pricequotation.constants import PMT



@optendersresource(
    name="{}:Tender Complaints".format(PMT),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=PMT,
    description="Tender complaints",
)
class TenderComplaintResource(BaseTenderComplaintResource):
    """ PriceQuotation complaint resource """
