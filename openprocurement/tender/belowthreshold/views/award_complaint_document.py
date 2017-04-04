# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    get_file,
    upload_file,
    update_file_content_type,
    json_view,
    context_unpack,
    APIResource,
    error_handler
)

from openprocurement.api.validation import (
    validate_file_update, validate_file_upload, validate_patch_document_data,
)

from openprocurement.tender.core.validation import (
    validate_status_and_role_for_complaint_document_operation,
    validate_award_complaint_document_operation_only_for_active_lots,
    validate_award_complaint_document_operation_not_in_allowed_status
)

from openprocurement.tender.core.utils import (
    save_tender, optendersresource, apply_patch,
)

from openprocurement.tender.belowthreshold.validation import (
    validate_complaint_document_update_not_by_author,
    validate_role_and_status_for_add_complaint_document
)


@optendersresource(name='belowThreshold:Tender Award Complaint Documents',
                   collection_path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents',
                   path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}',
                   procurementMethodType='belowThreshold',
                   description="Tender award complaint documents")
class TenderAwardComplaintDocumentResource(APIResource):

    @json_view(permission='view_tender')
    def collection_get(self):
        """Tender Award Complaint Documents List"""
        if self.request.params.get('all', ''):
            collection_data = [i.serialize("view") for i in self.context.documents]
        else:
            collection_data = sorted(dict([
                (i.id, i.serialize("view"))
                for i in self.context.documents
            ]).values(), key=lambda i: i['dateModified'])
        return {'data': collection_data}

    @json_view(permission='edit_complaint', validators=(validate_file_upload, validate_award_complaint_document_operation_not_in_allowed_status,
               validate_award_complaint_document_operation_only_for_active_lots, validate_role_and_status_for_add_complaint_document))
    def collection_post(self):
        """Tender Award Complaint Document Upload
        """
        document = upload_file(self.request)
        document.author = self.request.authenticated_role
        self.context.documents.append(document)
        if save_tender(self.request):
            self.LOGGER.info('Created tender award complaint document {}'.format(document.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_award_complaint_document_create'}, {'document_id': document.id}))
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=document_route, document_id=document.id, _query={})
            return {'data': document.serialize("view")}

    @json_view(permission='view_tender')
    def get(self):
        """Tender Award Complaint Document Read"""
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

    @json_view(validators=(validate_file_update, validate_complaint_document_update_not_by_author, validate_award_complaint_document_operation_not_in_allowed_status, validate_award_complaint_document_operation_only_for_active_lots,
               validate_status_and_role_for_complaint_document_operation), permission='edit_complaint')
    def put(self):
        """Tender Award Complaint Document Update"""
        document = upload_file(self.request)
        document.author = self.request.authenticated_role
        self.request.validated['complaint'].documents.append(document)
        if save_tender(self.request):
            self.LOGGER.info('Updated tender award complaint document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_award_complaint_document_put'}))
            return {'data': document.serialize("view")}

    @json_view(content_type="application/json", validators=(validate_patch_document_data, validate_complaint_document_update_not_by_author, validate_award_complaint_document_operation_not_in_allowed_status,
               validate_award_complaint_document_operation_only_for_active_lots, validate_status_and_role_for_complaint_document_operation), permission='edit_complaint')
    def patch(self):
        """Tender Award Complaint Document Update"""
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info('Updated tender award complaint document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_award_complaint_document_patch'}))
            return {'data': self.request.context.serialize("view")}
