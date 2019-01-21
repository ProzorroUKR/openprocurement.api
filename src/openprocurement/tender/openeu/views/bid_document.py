# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    get_file,
    upload_file,
    update_file_content_type,
    json_view,
    context_unpack,
    get_now,
    raise_operation_error
)
from openprocurement.api.validation import (
    validate_file_update,
    validate_file_upload,
    validate_patch_document_data,
)
from openprocurement.tender.core.validation import (
    validate_bid_document_operation_period,
    validate_bid_document_operation_with_award,
    validate_bid_document_operation_in_not_allowed_status
)
from openprocurement.tender.core.utils import (
    save_tender,
    apply_patch,
    optendersresource
)
from openprocurement.tender.openeu.utils import (
    bid_financial_documents_resource,
    bid_eligibility_documents_resource,
    bid_qualification_documents_resource,
)
from openprocurement.tender.openua.views.bid_document import (
    TenderUaBidDocumentResource
)
from openprocurement.tender.openeu.validation import (
    validate_update_bid_document_confidentiality,
    validate_add_bid_document_not_in_allowed_status,
    validate_update_bid_document_not_in_allowed_status
)


@optendersresource(name='aboveThresholdEU:Tender Bid Documents',
                   collection_path='/tenders/{tender_id}/bids/{bid_id}/documents',
                   path='/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}',
                   procurementMethodType='aboveThresholdEU',
                   description="Tender EU bidder documents")
class TenderEUBidDocumentResource(TenderUaBidDocumentResource):

    container = "documents"
    view_forbidden_states = ['active.tendering']
    view_forbidden_bid_states = ['invalid', 'deleted']

    def _doc_access_restricted(self, doc):
        is_bid_owner = self.request.authenticated_role == 'bid_owner'
        is_tender_owner = self.request.authenticated_role == 'tender_owner'
        return doc.confidentiality != 'public' and not (is_bid_owner or is_tender_owner)

    @json_view(permission='view_tender')
    def collection_get(self):
        """Tender Bid Documents List"""
        # TODO can't move validators because of self.view_forbidden_states
        if self.request.validated['tender_status'] in self.view_forbidden_states and self.request.authenticated_role != 'bid_owner':
            raise_operation_error(self.request, 'Can\'t view bid documents in current ({}) tender status'.format(self.request.validated['tender_status']))
        if self.context.status in self.view_forbidden_bid_states and self.request.authenticated_role != 'bid_owner':
            raise_operation_error(self.request, 'Can\'t view bid documents in current ({}) bid status'.format(self.context.status))
        if self.request.params.get('all', ''):
            collection_data = [i.serialize("restricted_view") if self._doc_access_restricted(i) else i.serialize("view")
                               for i in getattr(self.context, self.container)]
        else:
            collection_data = sorted(dict([(i.id, i.serialize("restricted_view") if self._doc_access_restricted(i) else i.serialize("view"))
                                           for i in getattr(self.context, self.container)]).values(), key=lambda i: i['dateModified'])
        return {'data': collection_data}

    @json_view(validators=(validate_file_upload, validate_bid_document_operation_in_not_allowed_status, validate_bid_document_operation_period, validate_bid_document_operation_with_award,
               validate_add_bid_document_not_in_allowed_status), permission='edit_bid')
    def collection_post(self):
        """Tender Bid Document Upload
        """
        document = upload_file(self.request)
        getattr(self.context, self.container).append(document)
        if self.request.validated['tender_status'] == 'active.tendering':
            self.request.validated['tender'].modified = False
        if save_tender(self.request):
            self.LOGGER.info('Created tender bid document {}'.format(document.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_bid_document_create'}, {'document_id': document.id}))
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=document_route, document_id=document.id, _query={})
            return {'data': document.serialize("view")}

    @json_view(permission='view_tender')
    def get(self):
        """Tender Bid Document Read"""
        # TODO can't move validators because of self.view_forbidden_states
        is_bid_owner = self.request.authenticated_role == 'bid_owner'
        if self.request.validated['tender_status'] in self.view_forbidden_states and not is_bid_owner:
            raise_operation_error(self.request, 'Can\'t view bid document in current ({}) tender status'.format(self.request.validated['tender_status']))
        if self.request.validated['bid'].status in self.view_forbidden_bid_states and self.request.authenticated_role != 'bid_owner':
            raise_operation_error(self.request, 'Can\'t view bid documents in current ({}) bid status'.format(self.request.validated['bid'].status))

        document = self.request.validated['document']
        if self.request.params.get('download'):
            if self._doc_access_restricted(document):
                raise_operation_error(self.request, 'Document download forbidden.')
            else:
                return get_file(self.request)
        document_data = document.serialize('restricted_view' if self._doc_access_restricted(document) else 'view')
        document_data['previousVersions'] = [i.serialize('restricted_view') if self._doc_access_restricted(i) else i.serialize('view')
                                             for i in self.request.validated['documents'] if i.url != document.url]
        return {'data': document_data}

    @json_view(content_type="application/json", validators=(validate_patch_document_data, validate_bid_document_operation_in_not_allowed_status, validate_bid_document_operation_period,
               validate_bid_document_operation_with_award, validate_update_bid_document_confidentiality, validate_update_bid_document_not_in_allowed_status), permission='edit_bid')
    def patch(self):
        """Tender Bid Document Update"""
        if self.request.validated['tender_status'] == 'active.tendering':
            self.request.validated['tender'].modified = False
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info('Updated tender bid document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_bid_document_patch'}))
            return {'data': self.request.context.serialize("view")}

    @json_view(validators=(validate_file_update, validate_bid_document_operation_in_not_allowed_status, validate_bid_document_operation_period, validate_bid_document_operation_with_award,
               validate_update_bid_document_confidentiality, validate_update_bid_document_not_in_allowed_status), permission='edit_bid')
    def put(self):
        """Tender Bid Document Update"""
        document = upload_file(self.request)
        getattr(self.request.validated['bid'], self.container).append(document)
        if self.request.validated['tender_status'] == 'active.tendering':
            self.request.validated['tender'].modified = False
        if save_tender(self.request):
            self.LOGGER.info('Updated tender bid document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_bid_document_put'}))
            return {'data': document.serialize("view")}


@bid_financial_documents_resource(
    name='aboveThresholdEU:Tender Bid Financial Documents',
    collection_path='/tenders/{tender_id}/bids/{bid_id}/financial_documents',
    path='/tenders/{tender_id}/bids/{bid_id}/financial_documents/{document_id}',
    procurementMethodType='aboveThresholdEU',
    description="Tender EU bidder financial documents")
class TenderEUBidFinancialDocumentResource(TenderEUBidDocumentResource):
    """ Tender EU Bid Financial Documents """

    container = "financialDocuments"
    view_forbidden_states = ['active.tendering', 'active.pre-qualification',
                             'active.pre-qualification.stand-still', 'active.auction']
    view_forbidden_bid_states = ['invalid', 'deleted', 'invalid.pre-qualification', 'unsuccessful']

@bid_eligibility_documents_resource(name='aboveThresholdEU:Tender Bid Eligibility Documents',
    collection_path='/tenders/{tender_id}/bids/{bid_id}/eligibility_documents',

    path='/tenders/{tender_id}/bids/{bid_id}/eligibility_documents/{document_id}',
    procurementMethodType='aboveThresholdEU',
    description="Tender EU bidder eligibility documents")
class TenderEUBidEligibilityDocumentResource(TenderEUBidFinancialDocumentResource):
    """ Tender EU Bid Eligibility Documents """
    container = "eligibilityDocuments"
    view_forbidden_states = ['active.tendering']
    view_forbidden_bid_states = ['invalid', 'deleted']


@bid_qualification_documents_resource(name='aboveThresholdEU:Tender Bid Qualification Documents',
    collection_path='/tenders/{tender_id}/bids/{bid_id}/qualification_documents',
    path='/tenders/{tender_id}/bids/{bid_id}/qualification_documents/{document_id}',
    procurementMethodType='aboveThresholdEU',
    description="Tender EU bidder qualification documents")
class TenderEUBidQualificationDocumentResource(TenderEUBidFinancialDocumentResource):
    """ Tender EU Bid Qualification Documents """
    container = "qualificationDocuments"
