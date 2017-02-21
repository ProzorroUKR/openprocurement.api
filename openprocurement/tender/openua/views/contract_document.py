# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.views.contract_document import TenderAwardContractDocumentResource


@optendersresource(name='Tender UA Contract Documents',
            collection_path='/tenders/{tender_id}/contracts/{contract_id}/documents',
            path='/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}',
            procurementMethodType='aboveThresholdUA',
            description="Tender contract documents")
class TenderUaAwardContractDocumentResource(TenderAwardContractDocumentResource):

    def validate_contract_document(self, operation):
        if self.request.validated['tender_status'] not in ['active.qualification', 'active.awarded']:
            self.request.errors.add('body', 'data', 'Can\'t {} document in current ({}) tender status'.format(operation, self.request.validated['tender_status']))
            self.request.errors.status = 403
            return
        if any([i.status != 'active' for i in self.request.validated['tender'].lots if i.id in [a.lotID for a in self.request.validated['tender'].awards if a.id == self.request.validated['contract'].awardID]]):
            self.request.errors.add('body', 'data', 'Can {} document only in active lot status'.format(operation))
            self.request.errors.status = 403
            return
        if self.request.validated['contract'].status not in ['pending', 'active']:
            self.request.errors.add('body', 'data', 'Can\'t {} document in current contract status'.format(operation))
            self.request.errors.status = 403
            return
        if any([any([c.status == 'accepted' for c in i.complaints]) for i in self.request.validated['tender'].awards if i.lotID in [a.lotID for a in self.request.validated['tender'].awards if a.id == self.request.validated['contract'].awardID]]):
            self.request.errors.add('body', 'data', 'Can\'t {} document with accepted complaint')
            self.request.errors.status = 403
            return
        return True
