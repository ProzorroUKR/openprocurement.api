# -*- coding: utf-8 -*-
from openprocurement.api.views.award_document import TenderAwardDocumentResource
from openprocurement.api.utils import opresource


@opresource(name='Tender UA Award Documents',
            collection_path='/tenders/{tender_id}/awards/{award_id}/documents',
            path='/tenders/{tender_id}/awards/{award_id}/documents/{document_id}',
            procurementMethodType='aboveThresholdUA',
            description="Tender award documents")
class TenderUaAwardDocumentResource(TenderAwardDocumentResource):

    def validate_award_document(self, operation):
        if self.request.validated['tender_status'] != 'active.qualification':
            self.request.errors.add('body', 'data', 'Can\'t {} document in current ({}) tender status'.format(operation, self.request.validated['tender_status']))
            self.request.errors.status = 403
            return
        if any([i.status != 'active' for i in self.request.validated['tender'].lots if i.id == self.request.validated['award'].lotID]):
            self.request.errors.add('body', 'data', 'Can {} document only in active lot status'.format(operation))
            self.request.errors.status = 403
            return
        if any([any([c.status == 'accepted' for c in i.complaints]) for i in self.request.validated['tender'].awards if i.lotID == self.request.validated['award'].lotID]):
            self.request.errors.add('body', 'data', 'Can\'t {} document with accepted complaint')
            self.request.errors.status = 403
            return
        if operation == 'update' and self.request.authenticated_role != (self.context.author or 'tender_owner'):
            self.request.errors.add('url', 'role', 'Can update document only author')
            self.request.errors.status = 403
            return
        return True
