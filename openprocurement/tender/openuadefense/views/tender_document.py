# -*- coding: utf-8 -*-
from openprocurement.api.models import get_now
from openprocurement.api.utils import opresource
from openprocurement.tender.openuadefense.utils import calculate_business_date
from openprocurement.tender.openua.views.tender_document import TenderUaDocumentResource as TenderDocumentResource
from openprocurement.tender.openuadefense.models import TENDERING_EXTRA_PERIOD


@opresource(name='Tender UA.defense Documents',
            collection_path='/tenders/{tender_id}/documents',
            path='/tenders/{tender_id}/documents/{document_id}',
            procurementMethodType='aboveThresholdUA.defense',
            description="Tender UA.defense related binary files (PDFs, etc.)")
class TenderUaDocumentResource(TenderDocumentResource):

    def validate_update_tender(self, operation):
        if self.request.authenticated_role != 'auction' and self.request.validated['tender_status'] != 'active.tendering' or \
           self.request.authenticated_role == 'auction' and self.request.validated['tender_status'] not in ['active.auction', 'active.qualification']:
            self.request.errors.add('body', 'data', 'Can\'t {} document in current ({}) tender status'.format(operation, self.request.validated['tender_status']))
            self.request.errors.status = 403
            return
        if self.request.validated['tender_status'] == 'active.tendering' and calculate_business_date(get_now(), TENDERING_EXTRA_PERIOD, self.request.validated['tender'], True) > self.request.validated['tender'].tenderPeriod.endDate:
            self.request.errors.add('body', 'data', 'tenderPeriod should be extended by {0.days} working days'.format(TENDERING_EXTRA_PERIOD))
            self.request.errors.status = 403
            return
        if operation == 'update' and self.request.authenticated_role != (self.context.author or 'tender_owner'):
            self.request.errors.add('url', 'role', 'Can update document only author')
            self.request.errors.status = 403
            return
        return True
