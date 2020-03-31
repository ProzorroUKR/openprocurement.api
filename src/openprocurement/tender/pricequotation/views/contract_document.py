# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.views.contract_document\
    import TenderAwardContractDocumentResource
from openprocurement.tender.pricequotation.constants import PMT


@optendersresource(
    name="{}:Tender Contract Documents".format(PMT),
    collection_path="/tenders/{tender_id}/contracts/{contract_id}/documents",
    path="/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}",
    procurementMethodType=PMT,
    description="Tender contract documents",
)
class PQTenderAwardContractDocumentResource(TenderAwardContractDocumentResource):
    """
    """
