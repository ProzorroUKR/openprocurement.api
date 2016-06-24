# -*- coding: utf-8 -*-
from openprocurement.contracting.api.utils import (
    save_contract,
    contractingresource,
    apply_patch,
)
from openprocurement.api.utils import (
    upload_file,
    update_file_content_type,
    get_file,
    context_unpack,
    APIResource,
    json_view
)
from openprocurement.api.validation import (
    validate_file_update,
    validate_file_upload,
    validate_patch_document_data,
)


@contractingresource(name='Contract Documents',
                     collection_path='/contracts/{contract_id}/documents',
                     path='/contracts/{contract_id}/documents/{document_id}',
                     description="Contract related binary files (PDFs, etc.)")
class ContractsDocumentResource(APIResource):

    @json_view(permission='view_contract')
    def collection_get(self):
        """Contract Documents List"""
        if self.request.params.get('all', ''):
            collection_data = [i.serialize("view") for i in self.context.documents]
        else:
            collection_data = sorted(dict([
                (i.id, i.serialize("view"))
                for i in self.context.documents
            ]).values(), key=lambda i: i['dateModified'])
        return {'data': collection_data}

    @json_view(permission='upload_contract_documents', validators=(validate_file_upload,))
    def collection_post(self):
        """Contract Document Upload"""
        if self.request.validated['contract'].status != 'active':
            self.request.errors.add('body', 'data', 'Can\'t add document in current ({}) contract status'.format(
                self.request.validated['contract'].status))
            self.request.errors.status = 403
            return

        document = upload_file(self.request)
        self.context.documents.append(document)
        if save_contract(self.request):
            self.LOGGER.info('Created contract document {}'.format(document.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'contract_document_create'}, {'document_id': document.id}))
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=document_route, document_id=document.id, _query={})
            return {'data': document.serialize("view")}

    @json_view(permission='view_contract')
    def get(self):
        """Contract Document Read"""
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

    @json_view(permission='upload_contract_documents', validators=(validate_file_update,))
    def put(self):
        """Contract Document Update"""
        if self.request.validated['contract'].status != 'active':
            self.request.errors.add('body', 'data', 'Can\'t update document in current ({}) contract status'.format(
                self.request.validated['contract'].status))
            self.request.errors.status = 403
            return

        document = upload_file(self.request)
        self.request.validated['contract'].documents.append(document)
        if save_contract(self.request):
            self.LOGGER.info('Updated contract document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'contract_document_put'}))
            return {'data': document.serialize("view")}

    @json_view(content_type="application/json", permission='upload_contract_documents', validators=(validate_patch_document_data,))
    def patch(self):
        """Contract Document Update"""
        if self.request.validated['contract'].status != 'active':
            self.request.errors.add('body', 'data', 'Can\'t update document in current ({}) contract status'.format(
                self.request.validated['contract'].status))
            self.request.errors.status = 403
            return

        data = self.request.validated['data']
        if "relatedItem" in data and data.get('documentOf') == 'change':
            if not [1 for c in self.request.validated['contract'].changes if c.id == data['relatedItem'] and c.status == 'pending']:
                self.request.errors.add('body', 'data', 'Can\'t add document to \'active\' change')
                self.request.errors.status = 403
                return

        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info('Updated contract document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'contract_document_patch'}))
            return {'data': self.request.context.serialize("view")}
