# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.tender_document import TenderEUDocumentResource


# @optendersresource(
#     name="esco:Tender Documents",
#     collection_path="/tenders/{tender_id}/documents",
#     path="/tenders/{tender_id}/documents/{document_id}",
#     procurementMethodType="esco",
#     description="Tender ESCO related binary files (PDFs, etc.)",
# )
class TenderESCODocumentResource(TenderEUDocumentResource):
    """ Tender ESCO Document Resource """
