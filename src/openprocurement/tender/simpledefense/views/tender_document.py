# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openuadefense.views.tender_document import TenderUaDocumentResource as TenderDocumentResource


# @optendersresource(
#     name="simple.defense:Tender Documents",
#     collection_path="/tenders/{tender_id}/documents",
#     path="/tenders/{tender_id}/documents/{document_id}",
#     procurementMethodType="simple.defense",
#     description="Tender simple.defense related binary files (PDFs, etc.)",
# )
class TenderSimpleDefDocumentResource(TenderDocumentResource):
    pass
