# -*- coding: utf-8 -*-
from openprocurement.api.utils import raise_operation_error, error_handler
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.award_complaint_document import (
    TenderUaAwardComplaintDocumentResource
)
from openprocurement.tender.openua.constants import STATUS4ROLE


@optendersresource(name='negotiation:Tender Award Complaint Documents',
                   collection_path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents',
                   path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}',
                   procurementMethodType='negotiation',
                   description="Tender negotiation award complaint documents")
class TenderNegotiationAwardComplaintDocumentResource(TenderUaAwardComplaintDocumentResource):

    def validate_complaint_document(self, operation):
        """ TODO move validators
        This class is inherited from openua package, but validate_complaint_document function has different validators.
        For now, we have no way to use different validators on methods according to procedure type.
        """
        if operation == 'update' and self.request.authenticated_role != self.context.author:
            self.request.errors.add('url', 'role', 'Can update document only author')
            self.request.errors.status = 403
            raise error_handler(self.request.errors)
        if self.request.validated['tender_status'] != 'active':
            raise_operation_error(self.request, 'Can\'t {} document in current ({}) tender status'.format(operation, self.request.validated['tender_status']))
        if self.request.validated['complaint'].status not in STATUS4ROLE.get(self.request.authenticated_role, []):
            raise_operation_error(self.request, 'Can\'t {} document in current ({}) complaint status'.format(operation, self.request.validated['complaint'].status))
        return True


@optendersresource(name='negotiation.quick:Tender Award Complaint Documents',
                   collection_path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents',
                   path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}',
                   procurementMethodType='negotiation.quick',
                   description="Tender negotiation.quick award complaint documents")
class TenderNegotiationQuickAwardComplaintDocumentResource(TenderNegotiationAwardComplaintDocumentResource):
    """ Tender Negotiation Quick Award Complaint Document Resource """
