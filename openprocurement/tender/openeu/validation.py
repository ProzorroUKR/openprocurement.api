# -*- coding: utf-8 -*-
from openprocurement.api.utils import get_now, raise_operation_error
from openprocurement.api.validation import validate_data, OPERATIONS
from openprocurement.tender.openeu.models import Qualification

def validate_patch_qualification_data(request):
    return validate_data(request, Qualification, True)

# bids
def validate_view_bids_in_active_tendering(request):
    if request.validated['tender_status'] == 'active.tendering':
        raise_operation_error(request, 'Can\'t view {} in current ({}) tender status'.format('bid' if request.matchdict.get('bid_id') else 'bids', request.validated['tender_status']))

# bid document
def validate_add_bid_document_not_in_allowed_status(request):
    if request.context.status in ['invalid', 'unsuccessful', 'deleted']:
        raise_operation_error(request, 'Can\'t add document to \'{}\' bid'.format(request.context.status))


def validate_update_bid_document_confidentiality(request):
    if request.validated['tender_status'] != 'active.tendering' and 'confidentiality' in request.validated.get('data', {}):
        if request.context.confidentiality != request.validated['data']['confidentiality']:
            raise_operation_error(request, 'Can\'t update document confidentiality in current ({}) tender status'.format(request.validated['tender_status']))


def validate_update_bid_document_not_in_allowed_status(request):
    bid = getattr(request.context, "__parent__")
    if bid and bid.status in ['invalid', 'unsuccessful', 'deleted']:
        raise_operation_error(request, 'Can\'t update {} \'{}\' bid'.format('document in' if request.method == 'PUT' else 'document data for',bid.status))

# qualification
def validate_qualification_document_operation_not_in_allowed_status(request):
    if request.validated['tender_status'] != 'active.pre-qualification':
        raise_operation_error(request, 'Can\'t {} document in current ({}) tender status'.format(OPERATIONS.get(request.method), request.validated['tender_status']))


def validate_qualification_document_operation_not_in_pending(request):
    qualification = request.validated['qualification']
    if qualification.status != 'pending':
        raise_operation_error(request, 'Can\'t {} document in current qualification status'.format(OPERATIONS.get(request.method)))

# qualification complaint
def validate_qualification_update_not_in_pre_qualification(request):
    tender = request.validated['tender']
    if tender.status not in ['active.pre-qualification']:
        raise_operation_error(request, 'Can\'t update qualification in current ({}) tender status'.format(tender.status))


def validate_cancelled_qualification_update(request):
    if request.context.status == 'cancelled':
        raise_operation_error(request, 'Can\'t update qualification in current cancelled qualification status')


def validate_add_complaint_not_in_pre_qualification(request):
    tender = request.validated['tender']
    if tender.status not in ['active.pre-qualification.stand-still']:
        raise_operation_error(request, 'Can\'t add complaint in current ({}) tender status'.format(tender.status))


def validate_update_complaint_not_in_pre_qualification(request):
    tender = request.validated['tender']
    if tender.status not in ['active.pre-qualification', 'active.pre-qualification.stand-still']:
        raise_operation_error(request, 'Can\'t update complaint in current ({}) tender status'.format(tender.status))


def validate_update_qualification_complaint_only_for_active_lots(request):
    tender = request.validated['tender']
    if any([i.status != 'active' for i in tender.lots if i.id == request.validated['qualification'].lotID]):
        raise_operation_error(request, 'Can update complaint only in active lot status')


def validate_add_complaint_not_in_qualification_period(request):
    tender = request.validated['tender']
    if tender.qualificationPeriod and \
       (tender.qualificationPeriod.startDate and tender.qualificationPeriod.startDate > get_now() or
                tender.qualificationPeriod.endDate and tender.qualificationPeriod.endDate < get_now()):
        raise_operation_error(request, 'Can add complaint only in qualificationPeriod')
