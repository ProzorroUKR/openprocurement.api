# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.contract_document import (
    TenderUaAwardContractDocumentResource as TenderAwardContractDocumentResource,
)


# @optendersresource(
#     name="simple.defense:Tender Contract Documents",
#     collection_path="/tenders/{tender_id}/contracts/{contract_id}/documents",
#     path="/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}",
#     procurementMethodType="simple.defense",
#     description="Tender contract documents",
# )
class TenderSimpleDefAwardContractDocumentResource(TenderAwardContractDocumentResource):
    """ """
