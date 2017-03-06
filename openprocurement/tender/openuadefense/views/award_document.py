# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.award_document import (
    TenderUaAwardDocumentResource as BaseResource
)


@optendersresource(name='aboveThresholdUA.defense:Tender Award Documents',
                   collection_path='/tenders/{tender_id}/awards/{award_id}/documents',
                   path='/tenders/{tender_id}/awards/{award_id}/documents/{document_id}',
                   procurementMethodType='aboveThresholdUA.defense',
                   description="Tender award documents")
class TenderUaAwardDocumentResource(BaseResource):
    pass
