# -*- coding: utf-8 -*-
from openprocurement.api.validation import (
    validate_file_update,
    validate_file_upload,
    validate_patch_document_data,
)
from openprocurement.api.utils import (
    context_unpack,
    json_view,
    raise_operation_error,
    update_file_content_type,
    upload_file,
)
from openprocurement.tender.core.utils import apply_patch, save_tender
from openprocurement.tender.openua.views.contract_document import (
    TenderUaAwardContractDocumentResource as BaseResource
)

from openprocurement.tender.cfaua.utils import agreement_resource


@agreement_resource(name='closeFrameworkAgreementUA:Tender Agreement Documents',
                    collection_path='/tenders/{tender_id}/agreements/{agreement_id}/documents',
                    path='/tenders/{tender_id}/agreements/{agreement_id}/documents/{document_id}',
                    procurementMethodType='closeFrameworkAgreementUA',
                    description="Tender agreement documents")
class TenderAwardContractDocumentResource(BaseResource):
    """ Tender Award Agreement Document """

    def validate_agreement_document(self, operation):
        """ TODO move validators
        This class is inherited from below package, but validate_agreement_document function has different validators.
        For now, we have no way to use different validators on methods according to procedure type.
        """
        if self.request.validated['tender_status'] not in ['active.qualification', 'active.awarded']:
            raise_operation_error(
                self.request, 'Can\'t {} document in current ({}) tender status'.format(
                    operation, self.request.validated['tender_status']))
        if any([i.status != 'active'
                for i in self.request.validated['tender'].lots
                if i.id in [a.lotID
                            for a in self.request.validated['tender'].awards
                            if a.id in self.request.validated['agreement'].get_awards_id()]]):
            raise_operation_error(self.request, 'Can {} document only in active lot status'.format(operation))
        if self.request.validated['agreement'].status not in ['pending', 'active']:
            raise_operation_error(self.request, 'Can\'t {} document in current agreement status'.format(operation))
        if any([any([c.status == 'accepted' for c in i.complaints])
                for i in self.request.validated['tender'].awards
                if i.lotID in [a.lotID
                               for a in self.request.validated['tender'].awards
                               if a.id in self.request.validated['agreement'].get_awards_id()]]):
            raise_operation_error(self.request, 'Can\'t {} document with accepted complaint')
        return True

    @json_view(permission='edit_tender', validators=(validate_file_upload,))
    def collection_post(self):
        """ Tender Agreement Document Upload """
        if not self.validate_agreement_document('add'):
            return
        document = upload_file(self.request)
        self.context.documents.append(document)
        if save_tender(self.request):
            self.LOGGER.info('Created tender agreement document {}'.format(document.id),
                             extra=context_unpack(self.request,
                                                  {'MESSAGE_ID': 'tender_agreement_document_create'},
                                                  {'document_id': document.id}))
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = \
                self.request.current_route_url(_route_name=document_route, document_id=document.id, _query={})
            return {'data': document.serialize("view")}

    @json_view(validators=(validate_file_update,), permission='edit_tender')
    def put(self):
        """ Tender Agreement Document Update """
        if not self.validate_agreement_document('update'):
            return
        document = upload_file(self.request)
        self.request.validated['agreement'].documents.append(document)
        if save_tender(self.request):
            self.LOGGER.info('Updated tender agreement document {}'.format(self.request.context.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_agreement_document_put'}))
            return {'data': document.serialize("view")}

    @json_view(content_type="application/json", validators=(validate_patch_document_data,), permission='edit_tender')
    def patch(self):
        """ Tender Agreement Document Update """
        if not self.validate_agreement_document('update'):
            return
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info('Updated tender agreement document {}'.format(self.request.context.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_agreement_document_patch'}))
            return {'data': self.request.context.serialize("view")}
