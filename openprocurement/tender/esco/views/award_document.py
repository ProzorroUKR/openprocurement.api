# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.award_document import TenderUaAwardDocumentResource
from openprocurement.tender.openeu.views.award_document import TenderAwardDocumentResource as TenderEUAwardDocumentResource
from openprocurement.tender.limited.views.award_document import TenderAwardDocumentResource as TenderReportingAwardDocumentResource


@opresource(name='Tender ESCO UA Award Documents',
            collection_path='/tenders/{tender_id}/awards/{award_id}/documents',
            path='/tenders/{tender_id}/awards/{award_id}/documents/{document_id}',
            procurementMethodType='esco.UA',
            description="Tender ESCO UA Award documents")
class TenderESCOUAAwardDocumentResource(TenderUaAwardDocumentResource):
    """ Tender ESCO UA Award Document Resource """


@opresource(name='Tender ESCO EU Award Documents',
            collection_path='/tenders/{tender_id}/awards/{award_id}/documents',
            path='/tenders/{tender_id}/awards/{award_id}/documents/{document_id}',
            procurementMethodType='esco.EU',
            description="Tender ESCO EU Award documents")
class TenderESCOEUAwardDocumentResource(TenderEUAwardDocumentResource):
    """ Tender ESCO EU Award Document Resource """


@opresource(name='Tender ESCO Reporting Award Documents',
            collection_path='/tenders/{tender_id}/awards/{award_id}/documents',
            path='/tenders/{tender_id}/awards/{award_id}/documents/{document_id}',
            procurementMethodType='esco.reporting',
            description="Tender ESCO Reporting Award documents")
class TenderESCOReportingAwardDocumentResource(TenderReportingAwardDocumentResource):
    """ Tender ESCO Reporting Award Document Resource """
