# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.contract_document import TenderUaAwardContractDocumentResource as BaseResource


# @optendersresource(
#     name="aboveThresholdEU:Tender Contract Documents",
#     collection_path="/tenders/{tender_id}/contracts/{contract_id}/documents",
#     path="/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}",
#     procurementMethodType="aboveThresholdEU",
#     description="Tender contract documents",
# )
class TenderAwardContractDocumentResource(BaseResource):
    """ Tender Award Contract Document """
