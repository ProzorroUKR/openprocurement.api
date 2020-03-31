# -*- coding: utf-8 -*-
# from openprocurement.api.utils import json_view
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.views.lot import TenderLotResource
from openprocurement.tender.pricequotation.constants import PMT


@optendersresource(
    name="{}:Tender Lots".format(PMT),
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType=PMT,
    description="Tender limited negotiation quick lots",
)
class TenderLimitedNegotiationQuickLotResource(TenderLotResource):
    """
    PriceQuotation lot creation and updation
    """
