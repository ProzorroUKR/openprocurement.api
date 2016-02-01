# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.utils import opresource

from openprocurement.api.views.contract_document import TenderAwardContractDocumentResource as BaseResource

LOGGER = getLogger(__name__)


@opresource(name='Tender EU Contract Documents',
            collection_path='/tenders/{tender_id}/contracts/{contract_id}/documents',
            path='/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}',
            procurementMethodType='aboveThresholdEU',
            description="Tender contract documents")
class TenderAwardContractDocumentResource(BaseResource):
    """ Tender Award Contract Document """
