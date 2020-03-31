# -*- coding: utf-8 -*-

from openprocurement.tender.belowthreshold.views.award_complaint import\
    TenderAwardComplaintResource
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.pricequotation.constants import PMT


@optendersresource(
    name="{}:Tender Award Complaints".format(PMT),
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=PMT,
    description="Tender award complaints",
)
class PTTenderAwardComplaintResource(TenderAwardComplaintResource):
    """ PriceQuotation award complaint resource """
