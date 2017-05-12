# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.award_document import TenderAwardDocumentResource as TenderEUAwardDocumentResource


@optendersresource(name='esco.EU:Tender Award Documents',
                   collection_path='/tenders/{tender_id}/awards/{award_id}/documents',
                   path='/tenders/{tender_id}/awards/{award_id}/documents/{document_id}',
                   procurementMethodType='esco.EU',
                   description="Tender ESCO EU Award documents")
class TenderESCOEUAwardDocumentResource(TenderEUAwardDocumentResource):
    """ Tender ESCO EU Award Document Resource """
