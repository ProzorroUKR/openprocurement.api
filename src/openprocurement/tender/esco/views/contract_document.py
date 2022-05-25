# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.contract_document import (
    TenderAwardContractDocumentResource as TenderEUContractDocumentResource,
)


# @optendersresource(
#     name="esco:Tender Contract Documents",
#     collection_path="/tenders/{tender_id}/contracts/{contract_id}/documents",
#     path="/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}",
#     procurementMethodType="esco",
#     description="Tender ESCO Contract documents",
# )
class TenderESCOContractDocumentResource(TenderEUContractDocumentResource):
    """ Tender EU Contract Document Resource """
