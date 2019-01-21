# -*- coding: utf-8 -*-
from openprocurement.api.utils import raise_operation_error, error_handler
from openprocurement.tender.openeu.views.award_complaint_document import TenderEUAwardComplaintDocumentResource
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.openua.constants import STATUS4ROLE


@qualifications_resource(name='aboveThresholdEU:Tender Qualification Complaint Documents',
                         collection_path='/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/documents',
                         path='/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/documents/{document_id}',
                         procurementMethodType='aboveThresholdEU',
                         description="Tender qualification complaint documents")
class TenderEUQualificationComplaintDocumentResource(TenderEUAwardComplaintDocumentResource):
    def validate_complaint_document(self, operation):
        """ TODO move validators
        This class is inherited from openua package, but validate_complaint_document function has different validators.
        For now, we have no way to use different validators on methods according to procedure type.
        """
        if operation == 'update' and self.request.authenticated_role != self.context.author:
            self.request.errors.add('url', 'role', 'Can update document only author')
            self.request.errors.status = 403
            raise error_handler(self.request.errors)
        if self.request.validated['tender_status'] not in ['active.pre-qualification', 'active.pre-qualification.stand-still']:
            raise_operation_error(self.request, 'Can\'t {} document in current ({}) tender status'.format(operation, self.request.validated['tender_status']))
        if any([i.status != 'active' for i in self.request.validated['tender'].lots if i.id == self.request.validated['qualification'].lotID]):
            raise_operation_error(self.request, 'Can {} document only in active lot status'.format(operation))
        if self.request.validated['complaint'].status not in STATUS4ROLE.get(self.request.authenticated_role, []):
            raise_operation_error(self.request, 'Can\'t {} document in current ({}) complaint status'.format(operation, self.request.validated['complaint'].status))
        return True
