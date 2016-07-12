# -*- coding: utf-8 -*-
from openprocurement.api.models import get_now
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
from openprocurement.tender.openeu.utils import (
    bid_financial_documents_resource, bid_eligibility_documents_resource,
    bid_qualification_documents_resource,
)
from openprocurement.tender.openua.views.bid_document import TenderUaBidDocumentResource


@opresource(name='Tender EU Bid Documents',
            collection_path='/tenders/{tender_id}/bids/{bid_id}/documents',
            path='/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}',
            procurementMethodType='aboveThresholdEU',
            description="Tender EU bidder documents")
class TenderEUBidDocumentResource(TenderUaBidDocumentResource):

    container = "documents"
    view_forbidden_states = ['active.tendering']

    def _doc_access_restricted(self, doc):
        is_bid_owner = self.request.authenticated_role == 'bid_owner'
        is_tender_owner = self.request.authenticated_role == 'tender_owner'
        return doc.confidentiality != 'public' and not (is_bid_owner or is_tender_owner)

    @json_view(permission='view_tender')
    def collection_get(self):
        """Tender Bid Documents List"""
        if self.request.validated['tender_status'] in self.view_forbidden_states and self.request.authenticated_role != 'bid_owner':
            self.request.errors.add('body', 'data', 'Can\'t view bid documents in current ({}) tender status'.format(self.request.validated['tender_status']))
            self.request.errors.status = 403
            return
        if self.request.params.get('all', ''):
            collection_data = [i.serialize("restricted_view") if self._doc_access_restricted(i) else i.serialize("view")
                               for i in getattr(self.context, self.container)]
        else:
            collection_data = sorted(dict([(i.id, i.serialize("restricted_view") if self._doc_access_restricted(i) else i.serialize("view"))
                                           for i in getattr(self.context, self.container)]).values(), key=lambda i: i['dateModified'])
        return {'data': collection_data}

    @json_view(validators=(validate_file_upload,), permission='edit_bid')
    def collection_post(self):
        """Tender Bid Document Upload
        """
        if self.request.validated['tender_status'] not in ['active.tendering', 'active.qualification', 'active.awarded']:
            self.request.errors.add('body', 'data', 'Can\'t add document in current ({}) tender status'.format(self.request.validated['tender_status']))
            self.request.errors.status = 403
            return
        tender = self.request.validated['tender']
        if self.request.validated['tender_status'] == 'active.tendering' and (tender.tenderPeriod.startDate and get_now() < tender.tenderPeriod.startDate or get_now() > tender.tenderPeriod.endDate):
            self.request.errors.add('body', 'data', 'Document can be added only during the tendering period: from ({}) to ({}).'.format(tender.tenderPeriod.startDate and tender.tenderPeriod.startDate.isoformat(), tender.tenderPeriod.endDate.isoformat()))
            self.request.errors.status = 403
            return
        if self.request.validated['tender_status'] in ['active.qualification', 'active.awarded'] and \
                not [i for i in self.request.validated['tender'].awards if i.status in ['pending', 'active'] and i.bid_id == self.request.validated['bid_id']]:
            self.request.errors.add('body', 'data', 'Can\'t add document because award of bid is not in pending or active state')
            self.request.errors.status = 403
            return
        if self.context.status in ['invalid', 'unsuccessful', 'deleted']:
            self.request.errors.add('body', 'data', 'Can\'t add document to \'{}\' bid'.format(self.context.status))
            self.request.errors.status = 403
            return
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
        is_bid_owner = self.request.authenticated_role == 'bid_owner'
        if self.request.validated['tender_status'] in self.view_forbidden_states and not is_bid_owner:
            self.request.errors.add('body', 'data', 'Can\'t view bid document in current ({}) tender status'.format(self.request.validated['tender_status']))
            self.request.errors.status = 403
            return

        document = self.request.validated['document']
        if self.request.params.get('download'):
            if self._doc_access_restricted(document):
                self.request.errors.add('body', 'data', 'Document download forbidden.')
                self.request.errors.status = 403
                return
            else:
                return get_file(self.request)
        document_data = document.serialize('restricted_view' if self._doc_access_restricted(document) else 'view')
        document_data['previousVersions'] = [i.serialize('restricted_view') if self._doc_access_restricted(i) else i.serialize('view')
                                             for i in self.request.validated['documents'] if i.url != document.url]
        return {'data': document_data}

    @json_view(content_type="application/json", validators=(validate_patch_document_data,), permission='edit_bid')
    def patch(self):
        """Tender Bid Document Update"""
        if self.request.validated['tender_status'] not in ['active.tendering', 'active.qualification', 'active.awarded']:
            self.request.errors.add('body', 'data', 'Can\'t update document in current ({}) tender status'.format(self.request.validated['tender_status']))
            self.request.errors.status = 403
            return
        tender = self.request.validated['tender']
        if self.request.validated['tender_status'] == 'active.tendering' and (tender.tenderPeriod.startDate and get_now() < tender.tenderPeriod.startDate or get_now() > tender.tenderPeriod.endDate):
            self.request.errors.add('body', 'data', 'Document can be updated only during the tendering period: from ({}) to ({}).'.format(tender.tenderPeriod.startDate and tender.tenderPeriod.startDate.isoformat(), tender.tenderPeriod.endDate.isoformat()))
            self.request.errors.status = 403
            return
        if self.request.validated['tender_status'] in ['active.qualification', 'active.awarded'] and \
                not [i for i in self.request.validated['tender'].awards if i.status in ['pending', 'active'] and i.bid_id == self.request.validated['bid_id']]:
            self.request.errors.add('body', 'data', 'Can\'t update document because award of bid is not in pending or active state')
            self.request.errors.status = 403
            return
        if self.request.validated['tender_status'] != 'active.tendering' and 'confidentiality' in self.request.validated['data']:
            if self.context.confidentiality != self.request.validated['data']['confidentiality']:
                self.request.errors.add('body', 'data', 'Can\'t update document confidentiality in current ({}) tender status'.format(self.request.validated['tender_status']))
                self.request.errors.status = 403
                return
        bid = getattr(self.context, "__parent__")
        if bid and bid.status in ['invalid', 'unsuccessful', 'deleted']:
            self.request.errors.add('body', 'data', 'Can\'t update document data for \'{}\' bid'.format(bid.status))
            self.request.errors.status = 403
            return
        if self.request.validated['tender_status'] == 'active.tendering':
            self.request.validated['tender'].modified = False
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info('Updated tender bid document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_bid_document_patch'}))
            return {'data': self.request.context.serialize("view")}

    @json_view(validators=(validate_file_update,), permission='edit_bid')
    def put(self):
        """Tender Bid Document Update"""
        if self.request.validated['tender_status'] not in ['active.tendering', 'active.qualification', 'active.awarded']:
            self.request.errors.add('body', 'data', 'Can\'t update document in current ({}) tender status'.format(self.request.validated['tender_status']))
            self.request.errors.status = 403
            return
        tender = self.request.validated['tender']
        if self.request.validated['tender_status'] == 'active.tendering' and (tender.tenderPeriod.startDate and get_now() < tender.tenderPeriod.startDate or get_now() > tender.tenderPeriod.endDate):
            self.request.errors.add('body', 'data', 'Document can be updated only during the tendering period: from ({}) to ({}).'.format(tender.tenderPeriod.startDate and tender.tenderPeriod.startDate.isoformat(), tender.tenderPeriod.endDate.isoformat()))
            self.request.errors.status = 403
            return
        if self.request.validated['tender_status'] in ['active.qualification', 'active.awarded'] and \
                not [i for i in self.request.validated['tender'].awards if i.status in ['pending', 'active'] and i.bid_id == self.request.validated['bid_id']]:
            self.request.errors.add('body', 'data', 'Can\'t update document because award of bid is not in pending or active state')
            self.request.errors.status = 403
            return
        bid = getattr(self.context, "__parent__")
        if bid and bid.status in ['invalid', 'unsuccessful', 'deleted']:
            self.request.errors.add('body', 'data', 'Can\'t update document in \'{}\' bid'.format(bid.status))
            self.request.errors.status = 403
            return
        document = upload_file(self.request)
        getattr(self.request.validated['bid'], self.container).append(document)
        if self.request.validated['tender_status'] == 'active.tendering':
            self.request.validated['tender'].modified = False
        if save_tender(self.request):
            self.LOGGER.info('Updated tender bid document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_bid_document_put'}))
            return {'data': document.serialize("view")}


@bid_financial_documents_resource(
    name='Tender EU Bid Financial Documents',
    collection_path='/tenders/{tender_id}/bids/{bid_id}/financial_documents',
    path='/tenders/{tender_id}/bids/{bid_id}/financial_documents/{document_id}',
    procurementMethodType='aboveThresholdEU',
    description="Tender EU bidder financial documents")
class TenderEUBidFinancialDocumentResource(TenderEUBidDocumentResource):
    """ Tender EU Bid Financial Documents """

    container = "financialDocuments"
    view_forbidden_states = ['active.tendering', 'active.pre-qualification',
                             'active.pre-qualification.stand-still', 'active.auction']


@bid_eligibility_documents_resource(name='Tender EU Bid Eligibility Documents',
    collection_path='/tenders/{tender_id}/bids/{bid_id}/eligibility_documents',

    path='/tenders/{tender_id}/bids/{bid_id}/eligibility_documents/{document_id}',
    procurementMethodType='aboveThresholdEU',
    description="Tender EU bidder eligibility documents")
class TenderEUBidEligibilityDocumentResource(TenderEUBidFinancialDocumentResource):
    """ Tender EU Bid Eligibility Documents """
    container = "eligibilityDocuments"


@bid_qualification_documents_resource(name='Tender EU Bid Qualification Documents',
    collection_path='/tenders/{tender_id}/bids/{bid_id}/qualification_documents',
    path='/tenders/{tender_id}/bids/{bid_id}/qualification_documents/{document_id}',
    procurementMethodType='aboveThresholdEU',
    description="Tender EU bidder qualification documents")
class TenderEUBidQualificationDocumentResource(TenderEUBidFinancialDocumentResource):
    """ Tender EU Bid Qualification Documents """
    container = "qualificationDocuments"
