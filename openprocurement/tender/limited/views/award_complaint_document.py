# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.award_complaint_document import TenderUaAwardComplaintDocumentResource
from openprocurement.tender.openua.views.complaint_document import STATUS4ROLE


@opresource(name='Tender negotiation Award Complaint Documents',
            collection_path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents',
            path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}',
            procurementMethodType='negotiation',
            description="Tender negotiation award complaint documents")
class TenderNegotiationAwardComplaintDocumentResource(TenderUaAwardComplaintDocumentResource):

    def validate_complaint_document(self, operation):
        if operation == 'update' and self.request.authenticated_role != self.context.author:
            self.request.errors.add('url', 'role', 'Can update document only author')
            self.request.errors.status = 403
            return
        if self.request.validated['tender_status'] != 'active':
            self.request.errors.add('body', 'data', 'Can\'t {} document in current ({}) tender status'.format(operation, self.request.validated['tender_status']))
            self.request.errors.status = 403
            return
        if self.request.validated['complaint'].status not in STATUS4ROLE.get(self.request.authenticated_role, []):
            self.request.errors.add('body', 'data', 'Can\'t {} document in current ({}) complaint status'.format(operation, self.request.validated['complaint'].status))
            self.request.errors.status = 403
            return
        return True


@opresource(name='Tender negotiation.quick Award Complaint Documents',
            collection_path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents',
            path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}',
            procurementMethodType='negotiation.quick',
            description="Tender negotiation.quick award complaint documents")
class TenderNegotiationQuickAwardComplaintDocumentResource(TenderNegotiationAwardComplaintDocumentResource):
    pass
