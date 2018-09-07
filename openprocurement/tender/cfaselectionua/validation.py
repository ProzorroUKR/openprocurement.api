# -*- coding: utf-8 -*-
from iso8601 import parse_date
from copy import deepcopy

from openprocurement.api.utils import error_handler, raise_operation_error, get_now
from openprocurement.api.validation import OPERATIONS, validate_data, validate_json_data

from openprocurement.tender.cfaselectionua.utils import prepare_shortlistedFirms, prepare_bid_identifier
from openprocurement.tender.cfaselectionua.constants import TENDER_PERIOD_MINIMAL_DURATION


def validate_patch_tender_data(request):
    data = validate_json_data(request)
    return validate_data(request, type(request.tender), True, data)


# tender documents
def validate_document_operation_in_not_allowed_tender_status(request):
    if request.authenticated_role != 'auction' and request.validated['tender_status'] not in ['draft.pending', 'active.enquiries'] or \
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
        raise_operation_error(request, 'Can\'t view bid {} in current ({}) tender status'.format('document' if request.matchdict.get('document_id') else 'documents', request.validated['tender_status']))


def validate_bid_document_operation_in_not_allowed_tender_status(request):
    if request.validated['tender_status'] not in ['active.tendering', 'active.qualification']:
        raise_operation_error(request, 'Can\'t {} document in current ({}) tender status'.format(OPERATIONS.get(request.method), request.validated['tender_status']))


def validate_bid_document_operation_with_not_pending_award(request):
    if request.validated['tender_status'] == 'active.qualification' and not [i for i in request.validated['tender'].awards if i.status == 'pending' and i.bid_id == request.validated['bid_id']]:
        raise_operation_error(request, 'Can\'t {} document because award of bid is not in pending state'.format(OPERATIONS.get(request.method)))


# lot
def validate_lot_operation(request):
    tender = request.validated['tender']
    if tender.status not in ['draft.pending', 'active.enquiries']:
        raise_operation_error(request, 'Can\'t {} lot in current ({}) tender status'.format(OPERATIONS.get(request.method), tender.status))


# auction
def validate_auction_info_view(request):
    if request.validated['tender_status'] != 'active.auction':
        raise_operation_error(request, 'Can\'t get auction info in current ({}) tender status'.format(request.validated['tender_status']))


def validate_tender_auction_data(request):
    data = validate_patch_tender_data(request)
    tender = request.validated['tender']
    if tender.status != 'active.auction':
        raise_operation_error(request, 'Can\'t {} in current ({}) tender status'.format('report auction results' if request.method == 'POST' else 'update auction urls', tender.status))
    lot_id = request.matchdict.get('auction_lot_id')
    if tender.lots and any([i.status != 'active' for i in tender.lots if i.id == lot_id]):
        raise_operation_error(request, 'Can {} only in active lot status'.format('report auction results' if request.method == 'POST' else 'update auction urls'))
    if data is not None:
        bids = data.get('bids', [])
        tender_bids_ids = [i.id for i in tender.bids]
        if len(bids) != len(tender.bids):
            request.errors.add('body', 'bids', "Number of auction results did not match the number of tender bids")
            request.errors.status = 422
            raise error_handler(request.errors)
        if set([i['id'] for i in bids]) != set(tender_bids_ids):
            request.errors.add('body', 'bids', "Auction bids should be identical to the tender bids")
            request.errors.status = 422
            raise error_handler(request.errors)
        data['bids'] = [x for (y, x) in sorted(zip([tender_bids_ids.index(i['id']) for i in bids], bids))]
        if data.get('lots'):
            tender_lots_ids = [i.id for i in tender.lots]
            if len(data.get('lots', [])) != len(tender.lots):
                request.errors.add('body', 'lots', "Number of lots did not match the number of tender lots")
                request.errors.status = 422
                raise error_handler(request.errors)
            if set([i['id'] for i in data.get('lots', [])]) != set([i.id for i in tender.lots]):
                request.errors.add('body', 'lots', "Auction lots should be identical to the tender lots")
                request.errors.status = 422
                raise error_handler(request.errors)
            data['lots'] = [
                x if x['id'] == lot_id else {}
                for (y, x) in sorted(zip([tender_lots_ids.index(i['id']) for i in data.get('lots', [])], data.get('lots', [])))
            ]
        if tender.lots:
            for index, bid in enumerate(bids):
                if (getattr(tender.bids[index], 'status', 'active') or 'active') == 'active':
                    if len(bid.get('lotValues', [])) != len(tender.bids[index].lotValues):
                        request.errors.add('body', 'bids', [{u'lotValues': [u'Number of lots of auction results did not match the number of tender lots']}])
                        request.errors.status = 422
                        raise error_handler(request.errors)
                    for lot_index, lotValue in enumerate(tender.bids[index].lotValues):
                        if lotValue.relatedLot != bid.get('lotValues', [])[lot_index].get('relatedLot', None):
                            request.errors.add('body', 'bids', [{u'lotValues': [{u'relatedLot': ['relatedLot should be one of lots of bid']}]}])
                            request.errors.status = 422
                            raise error_handler(request.errors)
            for bid_index, bid in enumerate(data['bids']):
                if 'lotValues' in bid:
                    bid['lotValues'] = [
                        x if x['relatedLot'] == lot_id and (getattr(tender.bids[bid_index].lotValues[lotValue_index], 'status', 'active') or 'active') == 'active' else {}
                        for lotValue_index, x in enumerate(bid['lotValues'])
                    ]

    else:
        data = {}
    if request.method == 'POST':
        now = get_now().isoformat()
        if tender.lots:
            data['lots'] = [{'auctionPeriod': {'endDate': now}} if i.id == lot_id else {} for i in tender.lots]
        else:
            data['auctionPeriod'] = {'endDate': now}
    request.validated['data'] = data


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
    if request.context.status not in ['draft', 'claim', 'answered']:
        raise_operation_error(request, 'Can\'t update complaint in current ({}) status'.format(request.context.status))


# contract document
def validate_cancellation_document_operation_not_in_allowed_status(request):
    if request.validated['tender_status'] in ['complete', 'cancelled', 'unsuccessful']:
        raise_operation_error(request, 'Can\'t {} document in current ({}) tender status'.format(OPERATIONS.get(request.method), request.validated['tender_status']))


# patch agreement
def validate_agreement_operation_not_in_allowed_status(request):
    if request.validated['tender_status'] != 'draft.pending':
        raise_operation_error(request,
                              'Can\'t {} agreement in current ({}) tender status'.format(
                                  OPERATIONS.get(request.method), request.validated['tender_status']))


def validate_patch_agreement_data(request):
    model = type(request.tender).agreements.model_class
    return validate_data(request, model, True)


# tender
def validate_patch_tender_in_draft_pending(request):
    if request.validated['tender_src']['status'] == 'draft.pending' and \
            request.authenticated_role not in ('agreement_selection', 'Administrator'):
        raise_operation_error(request,
                              'Can\'t {} tender in current ({}) tender status'.format(
                                  OPERATIONS.get(request.method), request.validated['tender_status']))


def validate_tender_status_update_in_terminated_status(request):
    tender = request.context
    if request.authenticated_role != 'Administrator' and \
            tender.status in ('complete', 'unsuccessful', 'cancelled', 'draft.unsuccessful'):
        raise_operation_error(request, 'Can\'t update tender in current ({}) status'.format(tender.status))


def validate_json_data_in_active_enquiries(request):
    source = request.validated['data']
    tender = request.validated['tender_src']
    data = {}
    if 'tenderPeriod' in source and 'endDate' in source['tenderPeriod']:
        validate_patch_tender_tenderPeriod(request)
        data['tenderPeriod'] = {
            'endDate': source['tenderPeriod']['endDate']
        }
    if 'items' in source:
        items = tender['items']
        for item in source['items']:
            if 'quantity' in item:
                i = [i for i in items if i['id'] == item['id']][0]
                i['quantity'] = item['quantity']
        data['items'] = items
    return data
    

def validate_patch_tender_tenderPeriod(request):
    data = request.validated['data']
    startDate = data['tenderPeriod'].get('startDate')
    endDate = data['tenderPeriod'].get('endDate')

    if (startDate and endDate) and (parse_date(endDate) - parse_date(startDate)) < TENDER_PERIOD_MINIMAL_DURATION:
        raise_operation_error(request, 'tenderPeriod should last at least 3 days')
