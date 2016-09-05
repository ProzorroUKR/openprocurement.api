# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.award_document import TenderUaAwardDocumentResource as BaseResource


@opresource(name='Tender EU Award Documents',
            collection_path='/tenders/{tender_id}/awards/{award_id}/documents',
            path='/tenders/{tender_id}/awards/{award_id}/documents/{document_id}',
            procurementMethodType='aboveThresholdEU',
            description="Tender award documents")
class TenderAwardDocumentResource(BaseResource):
    """ Tender Award Document """
