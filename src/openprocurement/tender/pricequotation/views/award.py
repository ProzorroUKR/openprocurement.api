# -*- coding: utf-8 -*-

from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.views.award import\
    TenderAwardResource
from openprocurement.tender.pricequotation.constants import PMT


@optendersresource(
    name="{}:Tender Awards".format(PMT),
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType=PMT,
)
class PQTenderAwardResource(TenderAwardResource):
    """ PriceQuotation award resource """
