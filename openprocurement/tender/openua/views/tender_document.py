from openprocurement.api.utils import (
    upload_file, context_unpack, json_view,
    update_file_content_type, get_now, error_handler, raise_operation_error
)
from openprocurement.tender.core.utils import (
    save_tender,
    apply_patch,
    optendersresource,
    calculate_business_date
)
from openprocurement.api.validation import validate_file_upload, validate_file_update, validate_patch_document_data
from openprocurement.tender.core.validation import (
    validate_document_operation_in_not_allowed_period,
    validate_tender_document_update_not_by_author_or_tender_owner
)
from openprocurement.tender.belowthreshold.views.tender_document import TenderDocumentResource
from openprocurement.tender.openua.constants import TENDERING_EXTRA_PERIOD


@optendersresource(name='aboveThresholdUA:Tender Documents',
                   collection_path='/tenders/{tender_id}/documents',
                   path='/tenders/{tender_id}/documents/{document_id}',
                   procurementMethodType='aboveThresholdUA',
                   description="Tender UA related binary files (PDFs, etc.)")
class TenderUaDocumentResource(TenderDocumentResource):

    def validate_update_tender(self):
        """ TODO move validators
        This class is inherited in cd stage 2 package, but validate_update_tender function has different validators.
        For now, we have no way to use different validators on methods according to procedure type.
        """
        if self.request.validated['tender_status'] == 'active.tendering' and calculate_business_date(get_now(), TENDERING_EXTRA_PERIOD, self.request.validated['tender']) > self.request.validated['tender'].tenderPeriod.endDate:
            raise_operation_error(self.request, 'tenderPeriod should be extended by {0.days} days'.format(TENDERING_EXTRA_PERIOD))
        return True

    @json_view(permission='upload_tender_documents', validators=(validate_file_upload, validate_document_operation_in_not_allowed_period))
    def collection_post(self):
        """Tender Document Upload"""
        if not self.validate_update_tender():
            raise error_handler(self.request.errors)
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

    @json_view(permission='upload_tender_documents', validators=(validate_file_update, validate_document_operation_in_not_allowed_period,
               validate_tender_document_update_not_by_author_or_tender_owner))
    def put(self):
        """Tender Document Update"""
        if not self.validate_update_tender():
            raise error_handler(self.request.errors)
        document = upload_file(self.request)
        self.request.validated['tender'].documents.append(document)
        if self.request.authenticated_role == 'tender_owner' and self.request.validated['tender_status'] == 'active.tendering':
            self.request.validated['tender'].invalidate_bids_data()
        if save_tender(self.request):
            self.LOGGER.info('Updated tender document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_document_put'}))
            return {'data': document.serialize("view")}

    @json_view(content_type="application/json", permission='upload_tender_documents', validators=(validate_patch_document_data,
               validate_document_operation_in_not_allowed_period, validate_tender_document_update_not_by_author_or_tender_owner))
    def patch(self):
        """Tender Document Update"""
        if not self.validate_update_tender():
            raise error_handler(self.request.errors)
        if self.request.authenticated_role == 'tender_owner' and self.request.validated['tender_status'] == 'active.tendering':
            self.request.validated['tender'].invalidate_bids_data()
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info('Updated tender document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_document_patch'}))
            return {'data': self.request.context.serialize("view")}
