# -*- coding: utf-8 -*-
from openprocurement.api.utils import update_logging_context, error_handler
from openprocurement.api.validation import validate_data
from openprocurement.tender.core.validation import OPERATIONS
from openprocurement.tender.belowthreshold.utils import  check_document


def validate_bid_data(request):
    if not request.check_accreditation(request.tender.edit_accreditation):
        request.errors.add('procurementMethodType', 'accreditation', 'Broker Accreditation level does not permit bid creation')
        request.errors.status = 403
        return
    if request.tender.get('mode', None) is None and request.check_accreditation('t'):
        request.errors.add('procurementMethodType', 'mode', 'Broker Accreditation level does not permit bid creation')
        request.errors.status = 403
        return
    update_logging_context(request, {'bid_id': '__new__'})
    model = type(request.tender).bids.model_class
    bid = validate_data(request, model)
    validated_bid = request.validated.get('bid')
    if validated_bid:
        if any([key == 'documents' or 'Documents' in key for key in validated_bid.keys()]):
            bid_documents = validate_bid_documents(request)
            if not bid_documents:
                return
            for documents_type, documents in bid_documents.items():
                validated_bid[documents_type] = documents
    return bid


def validate_patch_bid_data(request):
    model = type(request.tender).bids.model_class
    return validate_data(request, model, True)


def validate_award_data(request):
    update_logging_context(request, {'award_id': '__new__'})
    model = type(request.tender).awards.model_class
    return validate_data(request, model)


def validate_patch_award_data(request):
    model = type(request.tender).awards.model_class
    return validate_data(request, model, True)


def validate_cancellation_data(request):
    update_logging_context(request, {'cancellation_id': '__new__'})
    model = type(request.tender).cancellations.model_class
    return validate_data(request, model)


def validate_patch_cancellation_data(request):
    model = type(request.tender).cancellations.model_class
    return validate_data(request, model, True)


def validate_contract_data(request):
    update_logging_context(request, {'contract_id': '__new__'})
    model = type(request.tender).contracts.model_class
    return validate_data(request, model)


def validate_patch_contract_data(request):
    model = type(request.tender).contracts.model_class
    return validate_data(request, model, True)


def validate_bid_documents(request):
    bid_documents = [key for key in request.validated['bid'].keys() if key == 'documents' or 'Documents' in key]
    documents = {}
    for doc_type in bid_documents:
        documents[doc_type] = []
        for document in request.validated['bid'][doc_type]:
            model = getattr(type(request.validated['bid']), doc_type).model_class
            document = model(document)
            document.validate()
            route_kwargs = {'bid_id': request.validated['bid'].id}
            document = check_document(request, document, doc_type, route_kwargs)
            documents[doc_type].append(document)
    return documents

# tender documents
def validate_document_operation_in_not_allowed_tender_status(request):
    if request.authenticated_role != 'auction' and request.validated['tender_status'] != 'active.enquiries' or \
       request.authenticated_role == 'auction' and request.validated['tender_status'] not in ['active.auction', 'active.qualification']:
        request.errors.add('body', 'data', 'Can\'t {} document in current ({}) tender status'.format(OPERATIONS.get(request.method), request.validated['tender_status']))
        request.errors.status = 403
        raise error_handler(request.errors)

#bids
def validate_view_bids(request):
    if request.validated['tender_status'] in ['active.tendering', 'active.auction']:
        request.errors.add('body', 'data', 'Can\'t view bids in current ({}) tender status'.format(request.validated['tender_status']))
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_update_bid_status(request):
    if request.authenticated_role != 'Administrator':
        bid_status_to = request.validated['data'].get("status")
        if bid_status_to != request.context.status and bid_status_to != "active":
            request.errors.add('body', 'bid', 'Can\'t update bid to ({}) status'.format(bid_status_to))
            request.errors.status = 403
            raise error_handler(request.errors)

# bid documents
def validate_view_bid_document(request):
    if request.validated['tender_status'] in ['active.tendering', 'active.auction'] and request.authenticated_role != 'bid_owner':
        request.errors.add('body', 'data', 'Can\'t view bid {} in current ({}) tender status'.format('document' if 'document_id' in request.matchdict else 'documents',request.validated['tender_status']))
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_bid_document_operation_in_not_allowed_tender_status(request):
    if request.validated['tender_status'] not in ['active.tendering', 'active.qualification']:
        request.errors.add('body', 'data', 'Can\'t {} document in current ({}) tender status'.format(OPERATIONS.get(request.method), request.validated['tender_status']))
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_bid_document_operation_with_not_pending_award(request):
    if request.validated['tender_status'] == 'active.qualification' and not [i for i in request.validated['tender'].awards if i.status == 'pending' and i.bid_id == request.validated['bid_id']]:
        request.errors.add('body', 'data', 'Can\'t {} document because award of bid is not in pending state'.format(OPERATIONS.get(request.method)))
        request.errors.status = 403
        raise error_handler(request.errors)

# question
def validate_add_question(request):
    tender = request.validated['tender']
    if tender.status != 'active.enquiries' or tender.enquiryPeriod.startDate and get_now() < tender.enquiryPeriod.startDate or get_now() > tender.enquiryPeriod.endDate:
        request.errors.add('body', 'data', 'Can add question only in enquiryPeriod')
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_update_question(request):
    tender = request.validated['tender']
    if tender.status != 'active.enquiries':
        request.errors.add('body', 'data', 'Can\'t update question in current ({}) tender status'.format(tender.status))
        request.errors.status = 403
        raise error_handler(request.errors)

# lot
def validate_lot_operation(request):
    tender = request.validated['tender']
    if tender.status not in ['active.enquiries']:
        request.errors.add('body', 'data', 'Can\'t {} lot in current ({}) tender status'.format(OPERATIONS.get(request.method), tender.status))
        request.errors.status = 403
        raise error_handler(request.errors)

# complaint
def validate_add_complaint_not_in_allowed_tender_status(request):
    tender = request.context
    if tender.status not in ['active.enquiries', 'active.tendering']:
        request.errors.add('body', 'data', 'Can\'t add complaint in current ({}) tender status'.format(tender.status))
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_update_complaint_not_in_allowed_tender_status(request):
    tender = request.validated['tender']
    if tender.status not in ['active.enquiries', 'active.tendering', 'active.auction', 'active.qualification', 'active.awarded']:
        request.errors.add('body', 'data', 'Can\'t update complaint in current ({}) tender status'.format(tender.status))
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_update_complaint_not_in_allowed_status(request):
    if request.context.status not in ['draft', 'claim', 'answered', 'pending']:
        request.errors.add('body', 'data', 'Can\'t update complaint in current ({}) status'.format(request.context.status))
        request.errors.status = 403
        raise error_handler(request.errors)

# complaint document
def validate_complaint_document_operation_not_in_allowed_status(request):
    if request.validated['tender_status'] not in ['active.enquiries', 'active.tendering', 'active.auction', 'active.qualification', 'active.awarded']:
        request.errors.add('body', 'data', 'Can\'t {} document in current ({}) tender status'.format(OPERATIONS.get(request.method), request.validated['tender_status']))
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_complaint_document_update_not_by_author(request):
    if request.authenticated_role != request.context.author:
        request.errors.add('url', 'role', 'Can update document only author')
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_role_and_status_for_add_complaint_document(request):
    roles = request.content_configurator.allowed_statuses_for_complaint_operations_for_roles
    if request.context.status not in roles.get(request.authenticated_role, []):
        request.errors.add('body', 'data', 'Can\'t add document in current ({}) complaint status'.format(request.context.status))
        request.errors.status = 403
        raise error_handler(request.errors)

# auction
def validate_auction_info_view(request):
    if request.validated['tender_status'] != 'active.auction':
        request.errors.add('body', 'data', 'Can\'t get auction info in current ({}) tender status'.format(request.validated['tender_status']))
        request.errors.status = 403
        raise error_handler(request.errors)

# award
def validate_create_award_not_in_allowed_period(request):
    tender = request.validated['tender']
    if tender.status != 'active.qualification':
        request.errors.add('body', 'data', 'Can\'t create award in current ({}) tender status'.format(tender.status))
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_create_award_only_for_active_lot(request):
    tender = request.validated['tender']
    award = request.validated['award']
    if any([i.status != 'active' for i in tender.lots if i.id == award.lotID]):
        request.errors.add('body', 'data', 'Can create award only in active lot status')
        request.errors.status = 403
        raise error_handler(request.errors)

# award complaint
def validate_award_complaint_update_not_in_allowed_status(request):
    if request.context.status not in ['draft', 'claim', 'answered', 'pending']:
        request.errors.add('body', 'data', 'Can\'t update complaint in current ({}) status'.format(request.context.status))
        request.errors.status = 403
        raise error_handler(request.errors)

# contract document
def validate_cancellation_document_operation_not_in_allowed_status(request):
    if request.validated['tender_status'] in ['complete', 'cancelled', 'unsuccessful']:
        request.errors.add('body', 'data', 'Can\'t {} document in current ({}) tender status'.format(OPERATIONS.get(request.method), request.validated['tender_status']))
        request.errors.status = 403
        raise error_handler(request.errors)
