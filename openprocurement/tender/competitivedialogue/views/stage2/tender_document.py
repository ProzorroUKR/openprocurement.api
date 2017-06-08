# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openeu.views.tender_document import TenderEUDocumentResource
from openprocurement.tender.openua.views.tender_document import TenderUaDocumentResource
from openprocurement.tender.competitivedialogue.models import STAGE_2_UA_TYPE, STAGE_2_EU_TYPE, STAGE2_STATUS
from openprocurement.tender.openua.utils import calculate_business_date
from openprocurement.tender.openua.models import TENDERING_EXTRA_PERIOD
from openprocurement.api.models import get_now

@opresource(name='Competitive Dialogue Stage 2 EU Documents',
            collection_path='/tenders/{tender_id}/documents',
            path='/tenders/{tender_id}/documents/{document_id}',
            procurementMethodType=STAGE_2_EU_TYPE,
            description="Competitive Dialogue Stage 2 EU related binary files (PDFs, etc.)")
class CompetitiveDialogueStage2EUDocumentResource(TenderEUDocumentResource):

   def validate_update_tender(self, operation):
        if self.request.authenticated_role != 'auction' and self.request.validated['tender_status'] not in ['active.tendering', STAGE2_STATUS] or \
           self.request.authenticated_role == 'auction' and self.request.validated['tender_status'] not in ['active.auction', 'active.qualification']:
            self.request.errors.add('body', 'data', 'Can\'t {} document in current ({}) tender status'.format(operation, self.request.validated['tender_status']))
            self.request.errors.status = 403
            return
        if self.request.validated['tender_status'] == 'active.tendering' and calculate_business_date(get_now(), TENDERING_EXTRA_PERIOD, self.request.validated['tender']) > self.request.validated['tender'].tenderPeriod.endDate:
            self.request.errors.add('body', 'data', 'tenderPeriod should be extended by {0.days} days'.format(TENDERING_EXTRA_PERIOD))
            self.request.errors.status = 403
            return
        if operation == 'update' and self.request.authenticated_role != (self.context.author or 'tender_owner'):
            self.request.errors.add('url', 'role', 'Can update document only author')
            self.request.errors.status = 403
            return
        return True
    


@opresource(name='Competitive Dialogue Stage 2 UA Documents',
            collection_path='/tenders/{tender_id}/documents',
            path='/tenders/{tender_id}/documents/{document_id}',
            procurementMethodType=STAGE_2_UA_TYPE,
            description="Competitive Dialogue Stage 2 UA related binary files (PDFs, etc.)")
class CompetitiveDialogueStage2UADocumentResource(TenderUaDocumentResource):
    pass
