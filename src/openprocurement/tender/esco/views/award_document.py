# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.award_document import (
    TenderAwardDocumentResource as TenderEUAwardDocumentResource,
)


# @optendersresource(
#     name="esco:Tender Award Documents",
#     collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
#     path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
#     procurementMethodType="esco",
#     description="Tender ESCO Award documents",
# )
class TenderESCOAwardDocumentResource(TenderEUAwardDocumentResource):
    """ Tender ESCO Award Document Resource """
