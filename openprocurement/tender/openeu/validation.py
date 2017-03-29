# -*- coding: utf-8 -*-
from openprocurement.api.utils import error_handler
from openprocurement.api.validation import validate_data
from openprocurement.tender.openeu.models import Qualification

def validate_patch_qualification_data(request):
    return validate_data(request, Qualification, True)

# bids
def validate_view_bids_in_active_tendering(request):
    if request.validated['tender_status'] == 'active.tendering':
        request.errors.add('body', 'data', 'Can\'t view bids in current ({}) tender status'.format(request.validated['tender_status']))
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_bid_status_update_not_to_pending(request):
    if request.authenticated_role != 'Administrator':
        bid_status_to = request.validated['data'].get("status", request.context.status)
        if bid_status_to != 'pending':
            request.errors.add('body', 'bid', 'Can\'t update bid to ({}) status'.format(bid_status_to))
            request.errors.status = 403
            raise error_handler(request.errors)

# bid document
def validate_add_bid_document_not_in_allowed_status(request):
    if request.context.status in ['invalid', 'unsuccessful', 'deleted']:
        request.errors.add('body', 'data', 'Can\'t add document to \'{}\' bid'.format(request.context.status))
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_update_bid_document_confidentiality(request):
    if request.validated['tender_status'] != 'active.tendering' and 'confidentiality' in request.validated.get('data', {}):
        if request.context.confidentiality != request.validated['data']['confidentiality']:
            request.errors.add('body', 'data', 'Can\'t update document confidentiality in current ({}) tender status'.format(request.validated['tender_status']))
            request.errors.status = 403
            raise error_handler(request.errors)


def validate_update_bid_document_not_in_allowed_status(request):
    bid = getattr(request.context, "__parent__")
    if bid and bid.status in ['invalid', 'unsuccessful', 'deleted']:
        request.errors.add('body', 'data', 'Can\'t update {} \'{}\' bid'.format('document in' if request.method == 'PUT' else 'document data for',bid.status))
        request.errors.status = 403
        raise error_handler(request.errors)
