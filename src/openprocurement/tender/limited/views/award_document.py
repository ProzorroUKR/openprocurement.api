# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    get_file, upload_file, update_file_content_type, json_view,
    context_unpack, APIResource
)
from openprocurement.tender.core.utils import (
    apply_patch, save_tender, optendersresource
)
from openprocurement.api.validation import (
    validate_file_update, validate_file_upload, validate_patch_document_data
)
from openprocurement.tender.limited.validation import (
    validate_award_document_add_not_in_pending,
    validate_document_operation_not_in_active
)


@optendersresource(name='reporting:Tender Award Documents',
                   collection_path='/tenders/{tender_id}/awards/{award_id}/documents',
                   path='/tenders/{tender_id}/awards/{award_id}/documents/{document_id}',
                   procurementMethodType='reporting',
                   description="Tender award documents")
class TenderAwardDocumentResource(APIResource):

    @json_view(permission='view_tender')
    def collection_get(self):
        """Tender Award Documents List"""
        award = self.request.validated['award']
        if self.request.params.get('all', ''):
            collection_data = [i.serialize("view") for i in award['documents']]
        else:
            collection_data = sorted(dict([
                (i.id, i.serialize("view"))
                for i in award['documents']
            ]).values(), key=lambda i: i['dateModified'])
        return {'data': collection_data}

    @json_view(validators=(validate_file_upload, validate_document_operation_not_in_active, validate_award_document_add_not_in_pending), permission='edit_tender')
    def collection_post(self):
        """Tender Award Document Upload
        """
        document = upload_file(self.request)
        self.request.validated['award'].documents.append(document)
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

    @json_view(validators=(validate_file_update, validate_document_operation_not_in_active), permission='edit_tender')
    def put(self):
        """Tender Award Document Update"""
        document = upload_file(self.request)
        self.request.validated['award'].documents.append(document)
        if save_tender(self.request):
            self.LOGGER.info('Updated tender award document {}'.format(self.request.context.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_award_document_put'}))
            return {'data': document.serialize("view")}

    @json_view(content_type="application/json", validators=(validate_patch_document_data, validate_document_operation_not_in_active), permission='edit_tender')
    def patch(self):
        """Tender Award Document Update"""
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info('Updated tender award document {}'.format(self.request.context.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_award_document_patch'}))
            return {'data': self.request.context.serialize("view")}


@optendersresource(name='negotiation:Tender Award Documents',
                   collection_path='/tenders/{tender_id}/awards/{award_id}/documents',
                   path='/tenders/{tender_id}/awards/{award_id}/documents/{document_id}',
                   procurementMethodType='negotiation',
                   description="Tender award documents")
class TenderNegotiationAwardDocumentResource(TenderAwardDocumentResource):
    """ Tender Negotiation Award Documents Resource """


@optendersresource(name='negotiation.quick:Tender Award Documents',
                   collection_path='/tenders/{tender_id}/awards/{award_id}/documents',
                   path='/tenders/{tender_id}/awards/{award_id}/documents/{document_id}',
                   procurementMethodType='negotiation.quick',
                   description="Tender award documents")
class TenderNegotiationQuickAwardDocumentResource(TenderNegotiationAwardDocumentResource):
    """ Tender Negotiation Quick Award Documents Resource """
