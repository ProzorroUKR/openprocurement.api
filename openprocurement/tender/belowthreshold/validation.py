# -*- coding: utf-8 -*-
from openprocurement.api.utils import update_logging_context, error_handler, raise_operation_error, check_document
from openprocurement.api.validation import validate_data, OPERATIONS


# tender documents
def validate_document_operation_in_not_allowed_tender_status(request):
    if request.authenticated_role != 'auction' and request.validated['tender_status'] != 'active.enquiries' or \
       request.authenticated_role == 'auction' and request.validated['tender_status'] not in ['active.auction', 'active.qualification']:
        raise_operation_error(request, 'Can\'t {} document in current ({}) tender status'.format(OPERATIONS.get(request.method), request.validated['tender_status']))

#bids
def validate_view_bids(request):
    if request.validated['tender_status'] in ['active.tendering', 'active.auction']:
        raise_operation_error(request, 'Can\'t view {} in current ({}) tender status'.format('bid' if request.matchdict.get('bid_id') else 'bids', request.validated['tender_status']))


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
        raise_operation_error(request, 'Can\'t view bid {} in current ({}) tender status'.format('document' if request.matchdict.get('document_id') else 'documents',request.validated['tender_status']))


def validate_bid_document_operation_in_not_allowed_tender_status(request):
    if request.validated['tender_status'] not in ['active.tendering', 'active.qualification']:
        raise_operation_error(request, 'Can\'t {} document in current ({}) tender status'.format(OPERATIONS.get(request.method), request.validated['tender_status']))


def validate_bid_document_operation_with_not_pending_award(request):
    if request.validated['tender_status'] == 'active.qualification' and not [i for i in request.validated['tender'].awards if i.status == 'pending' and i.bid_id == request.validated['bid_id']]:
        raise_operation_error(request, 'Can\'t {} document because award of bid is not in pending state'.format(OPERATIONS.get(request.method)))

# question
def validate_add_question(request):
    tender = request.validated['tender']
    if tender.status != 'active.enquiries' or tender.enquiryPeriod.startDate and get_now() < tender.enquiryPeriod.startDate or get_now() > tender.enquiryPeriod.endDate:
        raise_operation_error(request, 'Can add question only in enquiryPeriod')


def validate_update_question(request):
    tender = request.validated['tender']
    if tender.status != 'active.enquiries':
        raise_operation_error(request, 'Can\'t update question in current ({}) tender status'.format(tender.status))

# lot
def validate_lot_operation(request):
    tender = request.validated['tender']
    if tender.status not in ['active.enquiries']:
        raise_operation_error(request, 'Can\'t {} lot in current ({}) tender status'.format(OPERATIONS.get(request.method), tender.status))

# complaint
def validate_add_complaint_not_in_allowed_tender_status(request):
    tender = request.context
    if tender.status not in ['active.enquiries', 'active.tendering']:
        raise_operation_error(request, 'Can\'t add complaint in current ({}) tender status'.format(tender.status))


def validate_update_complaint_not_in_allowed_tender_status(request):
    tender = request.validated['tender']
    if tender.status not in ['active.enquiries', 'active.tendering', 'active.auction', 'active.qualification', 'active.awarded']:
        raise_operation_error(request, 'Can\'t update complaint in current ({}) tender status'.format(tender.status))


def validate_update_complaint_not_in_allowed_status(request):
    if request.context.status not in ['draft', 'claim', 'answered', 'pending']:
        raise_operation_error(request, 'Can\'t update complaint in current ({}) status'.format(request.context.status))

# complaint document
def validate_complaint_document_operation_not_in_allowed_status(request):
    if request.validated['tender_status'] not in ['active.enquiries', 'active.tendering', 'active.auction', 'active.qualification', 'active.awarded']:
        raise_operation_error(request, 'Can\'t {} document in current ({}) tender status'.format(OPERATIONS.get(request.method), request.validated['tender_status']))


def validate_role_and_status_for_add_complaint_document(request):
    roles = request.content_configurator.allowed_statuses_for_complaint_operations_for_roles
    if request.context.status not in roles.get(request.authenticated_role, []):
        raise_operation_error(request, 'Can\'t add document in current ({}) complaint status'.format(request.context.status))

# auction
def validate_auction_info_view(request):
    if request.validated['tender_status'] != 'active.auction':
        raise_operation_error(request, 'Can\'t get auction info in current ({}) tender status'.format(request.validated['tender_status']))

# award
def validate_create_award_not_in_allowed_period(request):
    tender = request.validated['tender']
    if tender.status != 'active.qualification':
        raise_operation_error(request, 'Can\'t create award in current ({}) tender status'.format(tender.status))


def validate_create_award_only_for_active_lot(request):
    tender = request.validated['tender']
    award = request.validated['award']
    if any([i.status != 'active' for i in tender.lots if i.id == award.lotID]):
        raise_operation_error(request, 'Can create award only in active lot status')

# award complaint
def validate_award_complaint_update_not_in_allowed_status(request):
    if request.context.status not in ['draft', 'claim', 'answered', 'pending']:
        raise_operation_error(request, 'Can\'t update complaint in current ({}) status'.format(request.context.status))

# contract document
def validate_cancellation_document_operation_not_in_allowed_status(request):
    if request.validated['tender_status'] in ['complete', 'cancelled', 'unsuccessful']:
        raise_operation_error(request, 'Can\'t {} document in current ({}) tender status'.format(OPERATIONS.get(request.method), request.validated['tender_status']))
