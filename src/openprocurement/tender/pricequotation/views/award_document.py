# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.views.award_document import\
    TenderAwardDocumentResource
from openprocurement.tender.pricequotation.constants import PMT


@optendersresource(
    name="{}:Tender Award Documents".format(PMT),
    collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
    procurementMethodType=PMT,
    description="Tender award documents",
)
class PQTenderAwardDocumentResource(TenderAwardDocumentResource):
    """ PriceQuotation award document resource """
    
