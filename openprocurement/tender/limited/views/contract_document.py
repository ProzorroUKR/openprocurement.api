# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    upload_file, update_file_content_type, json_view, context_unpack
)
from openprocurement.tender.core.utils import (
    apply_patch, save_tender, optendersresource
)

from openprocurement.api.validation import (
    validate_file_update, validate_file_upload, validate_patch_document_data
)
from openprocurement.tender.belowthreshold.views.contract_document import (
    TenderAwardContractDocumentResource as BaseTenderAwardContractDocumentResource
)
from openprocurement.tender.limited.validation import (
    validate_document_operation_not_in_active,
    validate_contract_document_operation_not_in_allowed_contract_status
)


@optendersresource(name='reporting:Tender Contract Documents',
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

    @json_view(permission='edit_tender', validators=(validate_file_upload, validate_document_operation_not_in_active, validate_contract_document_operation_not_in_allowed_contract_status))
    def collection_post(self):
        """Tender Contract Document Upload
        """
        document = upload_file(self.request)
        self.request.validated['contract'].documents.append(document)
        if save_tender(self.request):
            self.LOGGER.info('Created tender contract document {}'.format(document.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_contract_document_create'}, {'document_id': document.id}))
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=document_route, document_id=document.id, _query={})
            return {'data': document.serialize("view")}

    @json_view(validators=(validate_file_update, validate_document_operation_not_in_active, validate_contract_document_operation_not_in_allowed_contract_status), permission='edit_tender')
    def put(self):
        """Tender Contract Document Update"""
        document = upload_file(self.request)
        self.request.validated['contract'].documents.append(document)
        if save_tender(self.request):
            self.LOGGER.info('Created tender contract document {}'.format(self.request.context.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_contract_document_put'}))
            return {'data': document.serialize("view")}

    @json_view(content_type="application/json", validators=(validate_patch_document_data,validate_document_operation_not_in_active,
               validate_contract_document_operation_not_in_allowed_contract_status), permission='edit_tender')
    def patch(self):
        """Tender Contract Document Update"""
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info('Created tender contract document {}'.format(self.request.context.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_contract_document_patch'}))
            return {'data': self.request.context.serialize("view")}


@optendersresource(name='negotiation:Tender Contract Documents',
                   collection_path='/tenders/{tender_id}/contracts/{contract_id}/documents',
                   path='/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}',
                   procurementMethodType='negotiation',
                   description="Tender contract documents")
class TenderNegotiationAwardContractDocumentResource(TenderAwardContractDocumentResource):
    """ Tender Negotiation Award Contract Document Resource """


@optendersresource(name='negotiation.quick:Tender Contract Documents',
                   collection_path='/tenders/{tender_id}/contracts/{contract_id}/documents',
                   path='/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}',
                   procurementMethodType='negotiation.quick',
                   description="Tender contract documents")
class TenderNegotiationQuickAwardContractDocumentResource(TenderNegotiationAwardContractDocumentResource):
    """ Tender Negotiation Quick Award Contract Document Resource """
