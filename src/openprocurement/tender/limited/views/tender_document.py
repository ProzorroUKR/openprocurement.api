# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    get_file, upload_file, update_file_content_type, json_view, context_unpack,
    APIResource
)

from openprocurement.tender.core.utils import (
    save_tender, apply_patch, optendersresource
)

from openprocurement.api.validation import (
    validate_file_update, validate_file_upload, validate_patch_document_data
)

from openprocurement.tender.limited.validation import validate_operation_with_document_not_in_active_status

@optendersresource(name='reporting:Tender Documents',
                   collection_path='/tenders/{tender_id}/documents',
                   path='/tenders/{tender_id}/documents/{document_id}',
                   procurementMethodType='reporting',
                   description="Tender related binary files (PDFs, etc.)")
class TenderDocumentResource(APIResource):

    @json_view(permission='view_tender')
    def collection_get(self):
        """Tender Documents List"""
        tender = self.request.validated['tender']
        if self.request.params.get('all', ''):
            collection_data = [i.serialize("view") for i in tender['documents']]
        else:
            collection_data = sorted(dict([
                (i.id, i.serialize("view"))
                for i in tender['documents']
            ]).values(), key=lambda i: i['dateModified'])
        return {'data': collection_data}

    @json_view(permission='upload_tender_documents', validators=(validate_file_upload, validate_operation_with_document_not_in_active_status))
    def collection_post(self):
        """Tender Document Upload"""
        document = upload_file(self.request)
        self.request.validated['tender'].documents.append(document)
        if save_tender(self.request):
            self.LOGGER.info('Created tender document {}'.format(document.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_document_create'}, {'document_id': document.id}))
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=document_route, document_id=document.id, _query={})
            return {'data': document.serialize("view")}

    @json_view(permission='view_tender')
    def get(self):
        """Tender Document Read"""
        if self.request.params.get('download'):
            return get_file(self.request)
        document = self.request.validated['document']
        document_data = document.serialize("view")
        document_data['previousVersions'] = [
            i.serialize("view")
            for i in self.request.validated['documents']
            if i.url != document.url
        ]
        return {'data': document_data}

    @json_view(permission='upload_tender_documents', validators=(validate_file_update, validate_operation_with_document_not_in_active_status))
    def put(self):
        """Tender Document Update"""
        document = upload_file(self.request)
        self.request.validated['tender'].documents.append(document)
        if save_tender(self.request):
            self.LOGGER.info('Updated tender document {}'.format(self.request.context.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_document_put'}))
            return {'data': document.serialize("view")}

    @json_view(content_type="application/json", permission='upload_tender_documents', validators=(validate_patch_document_data, validate_operation_with_document_not_in_active_status))
    def patch(self):
        """Tender Document Update"""
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info('Updated tender document {}'.format(self.request.context.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_document_patch'}))
            return {'data': self.request.context.serialize("view")}


@optendersresource(name='negotiation:Tender Documents',
                   collection_path='/tenders/{tender_id}/documents',
                   path='/tenders/{tender_id}/documents/{document_id}',
                   procurementMethodType='negotiation',
                   description="Tender related binary files (PDFs, etc.)")
class TenderNegotiationDocumentResource(TenderDocumentResource):
    """ Tender Negotiation Document Resource """


@optendersresource(name='negotiation.quick:Tender Documents',
                   collection_path='/tenders/{tender_id}/documents',
                   path='/tenders/{tender_id}/documents/{document_id}',
                   procurementMethodType='negotiation.quick',
                   description="Tender related binary files (PDFs, etc.)")
class TenderNegotiationQuickDocumentResource(TenderNegotiationDocumentResource):
    """ Tender Negotiation Quick Document Resource """
