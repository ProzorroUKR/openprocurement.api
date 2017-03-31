# -*- coding: utf-8 -*-
from openprocurement.api.models import get_now
from openprocurement.api.utils import opresource, upload_file, context_unpack, save_tender, json_view, apply_patch, update_file_content_type
from openprocurement.api.validation import validate_file_upload, validate_file_update, validate_patch_document_data
from openprocurement.api.views.tender_document import TenderDocumentResource
from openprocurement.tender.openua.utils import calculate_business_date
from openprocurement.tender.openua.models import TENDERING_EXTRA_PERIOD


@opresource(name='Tender UA Documents',
            collection_path='/tenders/{tender_id}/documents',
            path='/tenders/{tender_id}/documents/{document_id}',
            procurementMethodType='aboveThresholdUA',
            description="Tender UA related binary files (PDFs, etc.)")
class TenderUaDocumentResource(TenderDocumentResource):

    def validate_update_tender(self, operation):
        if self.request.authenticated_role != 'auction' and self.request.validated['tender_status'] != 'active.tendering' or \
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

    @json_view(permission='upload_tender_documents', validators=(validate_file_upload,))
    def collection_post(self):
        """Tender Document Upload"""
        if not self.validate_update_tender('add'):
            return
        document = upload_file(self.request)
        document.author = self.request.authenticated_role
        self.context.documents.append(document)
        if self.request.authenticated_role == 'tender_owner' and self.request.validated['tender_status'] == 'active.tendering':
            self.context.invalidate_bids_data()
        if save_tender(self.request):
            self.LOGGER.info('Created tender document {}'.format(document.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_document_create'}, {'document_id': document.id}))
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=document_route, document_id=document.id, _query={})
            return {'data': document.serialize("view")}

    @json_view(permission='upload_tender_documents', validators=(validate_file_update,))
    def put(self):
        """Tender Document Update"""
        if not self.validate_update_tender('update'):
            return
        document = upload_file(self.request)
        self.request.validated['tender'].documents.append(document)
        if self.request.authenticated_role == 'tender_owner' and self.request.validated['tender_status'] == 'active.tendering':
            self.request.validated['tender'].invalidate_bids_data()
        if save_tender(self.request):
            self.LOGGER.info('Updated tender document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_document_put'}))
            return {'data': document.serialize("view")}

    @json_view(content_type="application/json", permission='upload_tender_documents', validators=(validate_patch_document_data,))
    def patch(self):
        """Tender Document Update"""
        if not self.validate_update_tender('update'):
            return
        if self.request.authenticated_role == 'tender_owner' and self.request.validated['tender_status'] == 'active.tendering':
            self.request.validated['tender'].invalidate_bids_data()
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info('Updated tender document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_document_patch'}))
            return {'data': self.request.context.serialize("view")}
