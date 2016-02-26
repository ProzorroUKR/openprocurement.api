# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.utils import (
    get_file,
    save_tender,
    upload_file,
    apply_patch,
    update_file_content_type,
    opresource,
    json_view,
    context_unpack,
)
from openprocurement.api.validation import (
    validate_file_update,
    validate_file_upload,
    validate_patch_document_data,
)
from openprocurement.api.views.contract_document import TenderAwardContractDocumentResource as BaseTenderAwardContractDocumentResource


LOGGER = getLogger(__name__)


@opresource(name='Tender Limited Contract Documents',
            collection_path='/tenders/{tender_id}/contracts/{contract_id}/documents',
            path='/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}',
            procurementMethodType='reporting',
            description="Tender contract documents")
class TenderAwardContractDocumentResource(BaseTenderAwardContractDocumentResource):

    @json_view(permission='view_tender')
    def collection_get(self):
        """Tender Contract Documents List"""
        contract = self.request.validated['contract']
        if self.request.params.get('all', ''):
            collection_data = [i.serialize("view") for i in contract['documents']]
        else:
            collection_data = sorted(dict([
                (i.id, i.serialize("view"))
                for i in contract['documents']
            ]).values(), key=lambda i: i['dateModified'])
        return {'data': collection_data}

    @json_view(permission='edit_tender', validators=(validate_file_upload,))
    def collection_post(self):
        """Tender Contract Document Upload
        """
        if self.request.validated['tender_status'] not in ['active']:
            self.request.errors.add('body', 'data', 'Can\'t add document in current ({}) tender status'.format(self.request.validated['tender_status']))
            self.request.errors.status = 403
            return
        contract = self.request.validated['contract']
        if contract.status not in ['pending', 'active']:
            self.request.errors.add('body', 'data', 'Can\'t add document in current contract status')
            self.request.errors.status = 403
            return
        document = upload_file(self.request)
        self.request.validated['contract'].documents.append(document)
        if save_tender(self.request):
            LOGGER.info('Created tender contract document {}'.format(document.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_contract_document_create'}, {'document_id': document.id}))
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=document_route, document_id=document.id, _query={})
            return {'data': document.serialize("view")}

    @json_view(validators=(validate_file_update,), permission='edit_tender')
    def put(self):
        """Tender Contract Document Update"""
        if self.request.validated['tender_status'] not in ['active']:
            self.request.errors.add('body', 'data', 'Can\'t update document in current ({}) tender status'.format(self.request.validated['tender_status']))
            self.request.errors.status = 403
            return
        contract = self.request.validated['contract']
        if contract.status not in ['pending', 'active']:
            self.request.errors.add('body', 'data', 'Can\'t update document in current contract status')
            self.request.errors.status = 403
            return
        document = upload_file(self.request)
        self.request.validated['contract'].documents.append(document)
        if save_tender(self.request):
            LOGGER.info('Created tender contract document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_contract_document_put'}))
            return {'data': document.serialize("view")}

    @json_view(content_type="application/json", validators=(validate_patch_document_data,), permission='edit_tender')
    def patch(self):
        """Tender Contract Document Update"""
        if self.request.validated['tender_status'] not in ['active']:
            self.request.errors.add('body', 'data', 'Can\'t update document in current ({}) tender status'.format(self.request.validated['tender_status']))
            self.request.errors.status = 403
            return
        if self.request.validated['contract'].status not in ['pending', 'active']:
            self.request.errors.add('body', 'data', 'Can\'t update document in current contract status')
            self.request.errors.status = 403
            return
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            LOGGER.info('Created tender contract document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_contract_document_patch'}))
            return {'data': self.request.context.serialize("view")}


@opresource(name='Tender Negotiation Contract Documents',
            collection_path='/tenders/{tender_id}/contracts/{contract_id}/documents',
            path='/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}',
            procurementMethodType='negotiation',
            description="Tender contract documents")
class TenderNegotiationAwardContractDocumentResource(TenderAwardContractDocumentResource):
    """ Tender Negotiation Award Contract Document Resource """


@opresource(name='Tender Negotiation Quick Contract Documents',
            collection_path='/tenders/{tender_id}/contracts/{contract_id}/documents',
            path='/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}',
            procurementMethodType='negotiation.quick',
            description="Tender contract documents")
class TenderNegotiationQuickAwardContractDocumentResource(TenderNegotiationAwardContractDocumentResource):
    """ Tender Negotiation Quick Award Contract Document Resource """
