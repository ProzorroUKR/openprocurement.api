# -*- coding: utf-8 -*-
from openprocurement.api.utils import raise_operation_error, error_handler
from openprocurement.tender.belowthreshold.views.award_document import TenderAwardDocumentResource
from openprocurement.tender.core.utils import optendersresource


@optendersresource(name='aboveThresholdUA:Tender Award Documents',
                   collection_path='/tenders/{tender_id}/awards/{award_id}/documents',
                   path='/tenders/{tender_id}/awards/{award_id}/documents/{document_id}',
                   procurementMethodType='aboveThresholdUA',
                   description="Tender award documents")
class TenderUaAwardDocumentResource(TenderAwardDocumentResource):

    def validate_award_document(self, operation):
        """ TODO move validators
        This class is inherited from below package, but validate_award_document function has different validators.
        For now, we have no way to use different validators on methods according to procedure type.
        """
        if self.request.validated['tender_status'] != 'active.qualification':
            raise_operation_error(self.request, 'Can\'t {} document in current ({}) tender status'.format(operation, self.request.validated['tender_status']))
        if any([i.status != 'active' for i in self.request.validated['tender'].lots if i.id == self.request.validated['award'].lotID]):
            raise_operation_error(self.request, 'Can {} document only in active lot status'.format(operation))
        if any([any([c.status == 'accepted' for c in i.complaints]) for i in self.request.validated['tender'].awards if i.lotID == self.request.validated['award'].lotID]):
            raise_operation_error(self.request, 'Can\'t {} document with accepted complaint')
        if operation == 'update' and self.request.authenticated_role != (self.context.author or 'tender_owner'):
            self.request.errors.add('url', 'role', 'Can update document only author')
            self.request.errors.status = 403
            raise error_handler(self.request.errors)
        return True
