# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.tender_document import TenderUaDocumentResource


# @optendersresource(
#     name="closeFrameworkAgreementUA:Tender Documents",
#     collection_path="/tenders/{tender_id}/documents",
#     path="/tenders/{tender_id}/documents/{document_id}",
#     procurementMethodType="closeFrameworkAgreementUA",
#     description="Tender EU related binary files (PDFs, etc.)",
# )
class TenderEUDocumentResource(TenderUaDocumentResource):
    pass
