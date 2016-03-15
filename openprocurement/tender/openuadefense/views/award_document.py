# -*- coding: utf-8 -*-
from openprocurement.api.views.award_document import TenderAwardDocumentResource
from openprocurement.api.utils import opresource


@opresource(name='Tender UA.defense Award Documents',
            collection_path='/tenders/{tender_id}/awards/{award_id}/documents',
            path='/tenders/{tender_id}/awards/{award_id}/documents/{document_id}',
            procurementMethodType='aboveThresholdUA.defense',
            description="Tender award documents")
class TenderUaAwardDocumentResource(TenderAwardDocumentResource):
    pass
