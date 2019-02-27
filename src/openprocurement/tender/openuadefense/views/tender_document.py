# -*- coding: utf-8 -*-
from openprocurement.api.utils import get_now, raise_operation_error
from openprocurement.tender.core.utils import (
    optendersresource, calculate_business_date
)
from openprocurement.tender.openua.views.tender_document import TenderUaDocumentResource as TenderDocumentResource
from openprocurement.tender.openuadefense.constants import TENDERING_EXTRA_PERIOD


@optendersresource(name='aboveThresholdUA.defense:Tender Documents',
                   collection_path='/tenders/{tender_id}/documents',
                   path='/tenders/{tender_id}/documents/{document_id}',
                   procurementMethodType='aboveThresholdUA.defense',
                   description="Tender UA.defense related binary files (PDFs, etc.)")
class TenderUaDocumentResource(TenderDocumentResource):

    def validate_update_tender(self):
        """ TODO move validators
        This class is inherited from openua package, but validate_update_tender function has different validators (check using working days).
        For now, we have no way to use different validators on methods according to procedure type.
        """
        if self.request.validated['tender_status'] == 'active.tendering' and calculate_business_date(get_now(), TENDERING_EXTRA_PERIOD, self.request.validated['tender'], True) > self.request.validated['tender'].tenderPeriod.endDate:
            raise_operation_error(self.request, 'tenderPeriod should be extended by {0.days} working days'.format(TENDERING_EXTRA_PERIOD))
        return True
