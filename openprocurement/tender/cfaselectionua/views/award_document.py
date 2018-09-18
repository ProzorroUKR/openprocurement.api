# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    get_file,
    upload_file,
    update_file_content_type,
    json_view,
    context_unpack,
    APIResource,
)
from openprocurement.api.validation import (
    validate_file_update,
    validate_file_upload,
    validate_patch_document_data,
)

from openprocurement.tender.core.utils import (
    save_tender, optendersresource, apply_patch,
)
from openprocurement.tender.cfaselectionua.validation import validate_award_document

@optendersresource(name='closeFrameworkAgreementSelectionUA:Tender Award Documents',
                   collection_path='/tenders/{tender_id}/awards/{award_id}/documents',
                   path='/tenders/{tender_id}/awards/{award_id}/documents/{document_id}',
                   procurementMethodType='closeFrameworkAgreementSelectionUA',
                   description="Tender award documents")
class TenderAwardDocumentResource(APIResource):

    @json_view(permission='view_tender')
    def collection_get(self):
        """Tender Award Documents List"""
        if self.request.params.get('all', ''):
            collection_data = [i.serialize("view") for i in self.context.documents]
        else:
            collection_data = sorted(dict([
                (i.id, i.serialize("view"))
                for i in self.context.documents
            ]).values(), key=lambda i: i['dateModified'])
        return {'data': collection_data}

    @json_view(validators=(validate_file_upload, validate_award_document), permission='upload_tender_documents')
    def collection_post(self):
        """Tender Award Document Upload
        """
        document = upload_file(self.request)
        document.author = self.request.authenticated_role
        self.context.documents.append(document)
        if save_tender(self.request):
            self.LOGGER.info('Created tender award document {}'.format(document.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_award_document_create'}, {'document_id': document.id}))
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=document_route, document_id=document.id, _query={})
            return {'data': document.serialize("view")}

    @json_view(permission='view_tender')
    def get(self):
        """Tender Award Document Read"""
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

    @json_view(validators=(validate_file_update, validate_award_document), permission='edit_tender')
    def put(self):
        """Tender Award Document Update"""
        document = upload_file(self.request)
        self.request.validated['award'].documents.append(document)
        if save_tender(self.request):
            self.LOGGER.info('Updated tender award document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_award_document_put'}))
            return {'data': document.serialize("view")}

    @json_view(content_type="application/json", validators=(validate_patch_document_data, validate_award_document), permission='edit_tender')
    def patch(self):
        """Tender Award Document Update"""
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info('Updated tender award document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_award_document_patch'}))
            return {'data': self.request.context.serialize("view")}
