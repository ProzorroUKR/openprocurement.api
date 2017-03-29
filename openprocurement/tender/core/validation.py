# -*- coding: utf-8 -*-
from openprocurement.api.validation import validate_data, validate_json_data
from openprocurement.api.utils import get_now  # move
from openprocurement.api.utils import update_logging_context, error_handler # XXX tender context
from schematics.exceptions import ValidationError


def validate_tender_data(request):
    update_logging_context(request, {'tender_id': '__new__'})

    data = validate_json_data(request)

    model = request.tender_from_data(data, create=False)
    #if not request.check_accreditation(model.create_accreditation):
    #if not any([request.check_accreditation(acc) for acc in getattr(model, 'create_accreditations', [getattr(model, 'create_accreditation', '')])]):
    if not any([request.check_accreditation(acc) for acc in iter(str(model.create_accreditation))]):
        request.errors.add('procurementMethodType', 'accreditation', 'Broker Accreditation level does not permit tender creation')
        request.errors.status = 403
        raise error_handler(request.errors)
    data = validate_data(request, model, data=data)
    if data and data.get('mode', None) is None and request.check_accreditation('t'):
        request.errors.add('procurementMethodType', 'mode', 'Broker Accreditation level does not permit tender creation')
        request.errors.status = 403
        raise error_handler(request.errors)
    if data and data.get('procuringEntity', {}).get('kind', '') not in model.procuring_entity_kinds:
        request.errors.add('procuringEntity',
                           'kind',
                           '{kind!r} procuringEntity cannot publish this type of procedure. '
                           'Only {kinds} are allowed.'.format(kind=data.get('procuringEntity', {}).get('kind', ''), kinds=', '.join(model.procuring_entity_kinds)))
        request.errors.status = 403


def validate_patch_tender_data(request):
    data = validate_json_data(request)
    if request.context.status != 'draft':
        return validate_data(request, type(request.tender), True, data)
    default_status = type(request.tender).fields['status'].default
    if data.get('status') != default_status:
        request.errors.add('body', 'data', 'Can\'t update tender in current (draft) status')
        request.errors.status = 403
        raise error_handler(request.errors)
    request.validated['data'] = {'status': default_status}
    request.context.status = default_status


def validate_tender_auction_data(request):
    data = validate_patch_tender_data(request)
    tender = request.validated['tender']
    if tender.status != 'active.auction':
        request.errors.add('body', 'data', 'Can\'t {} in current ({}) tender status'.format('report auction results' if request.method == 'POST' else 'update auction urls', tender.status))
        request.errors.status = 403
        raise error_handler(request.errors)
    lot_id = request.matchdict.get('auction_lot_id')
    if tender.lots and any([i.status != 'active' for i in tender.lots if i.id == lot_id]):
        request.errors.add('body', 'data', 'Can {} only in active lot status'.format('report auction results' if request.method == 'POST' else 'update auction urls'))
        request.errors.status = 403
        raise error_handler(request.errors)
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


def validate_bid_data(request):
    if not request.check_accreditation(request.tender.edit_accreditation):
        request.errors.add('procurementMethodType', 'accreditation', 'Broker Accreditation level does not permit bid creation')
        request.errors.status = 403
        raise error_handler(request.errors)
    if request.tender.get('mode', None) is None and request.check_accreditation('t'):
        request.errors.add('procurementMethodType', 'mode', 'Broker Accreditation level does not permit bid creation')
        request.errors.status = 403
        raise error_handler(request.errors)
    update_logging_context(request, {'bid_id': '__new__'})
    model = type(request.tender).bids.model_class
    return validate_data(request, model)


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


def validate_question_data(request):
    if not request.check_accreditation(request.tender.edit_accreditation):
        request.errors.add('procurementMethodType', 'accreditation', 'Broker Accreditation level does not permit question creation')
        request.errors.status = 403
        raise error_handler(request.errors)
    if request.tender.get('mode', None) is None and request.check_accreditation('t'):
        request.errors.add('procurementMethodType', 'mode', 'Broker Accreditation level does not permit question creation')
        request.errors.status = 403
        raise error_handler(request.errors)
    update_logging_context(request, {'question_id': '__new__'})
    model = type(request.tender).questions.model_class
    return validate_data(request, model)


def validate_patch_question_data(request):
    model = type(request.tender).questions.model_class
    return validate_data(request, model, True)


def validate_complaint_data(request):
    if not request.check_accreditation(request.tender.edit_accreditation):
        request.errors.add('procurementMethodType', 'accreditation', 'Broker Accreditation level does not permit complaint creation')
        request.errors.status = 403
        raise error_handler(request.errors)
    if request.tender.get('mode', None) is None and request.check_accreditation('t'):
        request.errors.add('procurementMethodType', 'mode', 'Broker Accreditation level does not permit complaint creation')
        request.errors.status = 403
        raise error_handler(request.errors)
    update_logging_context(request, {'complaint_id': '__new__'})
    model = type(request.tender).complaints.model_class
    return validate_data(request, model)


def validate_patch_complaint_data(request):
    model = type(request.tender).complaints.model_class
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


def validate_lot_data(request):
    update_logging_context(request, {'lot_id': '__new__'})
    model = type(request.tender).lots.model_class
    return validate_data(request, model)


def validate_patch_lot_data(request):
    model = type(request.tender).lots.model_class
    return validate_data(request, model, True)


def validate_LotValue_value(tender, relatedLot, value):
    lots = [i for i in tender.lots if i.id == relatedLot]
    if not lots:
        return
    lot = lots[0]
    if lot.value.amount < value.amount:
        raise ValidationError(u"value of bid should be less than value of lot")
    if lot.get('value').currency != value.currency:
        raise ValidationError(u"currency of bid should be identical to currency of value of lot")
    if lot.get('value').valueAddedTaxIncluded != value.valueAddedTaxIncluded:
        raise ValidationError(u"valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of lot")

# tender
def validate_tender_status_update_in_terminated_status(request):
    tender = request.context
    if request.authenticated_role != 'Administrator' and tender.status in ['complete', 'unsuccessful', 'cancelled']:
        request.errors.add('body', 'data', 'Can\'t update tender in current ({}) status'.format(tender.status))
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_tender_status_update_not_in_pre_qualificaton(request):
    tender = request.context
    data = request.validated['data']
    if request.authenticated_role == 'tender_owner' and 'status' in data and data['status'] not in ['active.pre-qualification.stand-still', tender.status]:
        request.errors.add('body', 'data', 'Can\'t update tender status')
        request.errors.status = 403
        raise error_handler(request.errors)

# tender documents
def validate_document_operation_in_not_allowed_period(request):
    if request.authenticated_role != 'auction' and request.validated['tender_status'] != 'active.tendering' or \
        request.authenticated_role == 'auction' and request.validated['tender_status'] not in ['active.auction', 'active.qualification']:
        request.errors.add('body', 'data', 'Can\'t {} document in current ({}) tender status'.format('add' if request.method == 'POST' else 'update', request.validated['tender_status']))
        request.errors.status = 403
        raise error_handler(request.errors)

# bids
def validate_bid_operation_not_in_tendering(request):
    if request.validated['tender_status'] != 'active.tendering':
        operation = 'add' if request.method == 'POST' else 'delete'
        if request.authenticated_role != 'Administrator' and request.method in ('PUT', 'PATCH'):
            operation = 'update'
        request.errors.add('body', 'data', 'Can\'t {} bid in current ({}) tender status'.format(operation, request.validated['tender_status']))
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_bid_operation_period(request):
    tender = request.validated['tender']
    if tender.tenderPeriod.startDate and get_now() < tender.tenderPeriod.startDate or get_now() > tender.tenderPeriod.endDate:
        operation = 'added' if request.method == 'POST' else 'deleted'
        if request.authenticated_role != 'Administrator' and request.method in ('PUT', 'PATCH'):
            operation = 'updated'
        request.errors.add('body', 'data', 'Bid can be {} only during the tendering period: from ({}) to ({}).'.format(operation, tender.tenderPeriod.startDate and tender.tenderPeriod.startDate.isoformat(), tender.tenderPeriod.endDate.isoformat()))
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_update_deleted_bid(request):
    if request.context.status == 'deleted':
        request.errors.add('body', 'bid', 'Can\'t update bid in ({}) status'.format(request.context.status))
        request.errors.status = 403
        raise error_handler(request.errors)

# bid document
def validate_bid_document_operation_period(request):
    tender = request.validated['tender']
    if request.validated['tender_status'] == 'active.tendering' and (tender.tenderPeriod.startDate and get_now() < tender.tenderPeriod.startDate or get_now() > tender.tenderPeriod.endDate):
        request.errors.add('body', 'data', 'Document can be {} only during the tendering period: from ({}) to ({}).'.format('added' if request.method == 'POST' else 'updated',
            tender.tenderPeriod.startDate and tender.tenderPeriod.startDate.isoformat(), tender.tenderPeriod.endDate.isoformat()))
        request.errors.status = 403
        raise error_handler(request.errors)

# for openua, openeu
def validate_bid_document_operation_in_not_allowed_status(request):
    if request.validated['tender_status'] not in ['active.tendering', 'active.qualification', 'active.awarded']:
        request.errors.add('body', 'data', 'Can\'t {} document in current ({}) tender status'.format('add' if request.method == 'POST' else 'update', request.validated['tender_status']))
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_bid_document_operation_with_award(request):
    if request.validated['tender_status'] in ['active.qualification', 'active.awarded'] and \
            not [i for i in request.validated['tender'].awards if i.status in ['pending', 'active'] and i.bid_id == request.validated['bid_id']]:
        request.errors.add('body', 'data', 'Can\'t {} document because award of bid is not in pending or active state'.format('add' if request.method == 'POST' else 'update'))
        request.errors.status = 403
        raise error_handler(request.errors)

# awards
def validate_update_award_in_not_allowed_status(request):
    tender = request.validated['tender']
    if tender.status not in ['active.qualification', 'active.awarded']:
        request.errors.add('body', 'data', 'Can\'t update award in current ({}) tender status'.format(tender.status))
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_update_award_only_for_active_lots(request):
    tender = request.validated['tender']
    award = request.context
    if any([i.status != 'active' for i in tender.lots if i.id == award.lotID]):
        request.errors.add('body', 'data', 'Can update award only in active lot status')
        request.errors.status = 403
        raise error_handler(request.errors)

# award complaint
def validate_award_complaint_operation_not_in_allowed_status(request):
    tender = request.validated['tender']
    if tender.status not in ['active.qualification', 'active.awarded']:
        request.errors.add('body', 'data', 'Can\'t {} complaint in current ({}) tender status'.format('add' if request.method == 'POST' else 'update', tender.status))
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_award_complaint_add_only_for_active_lots(request):
    tender = request.validated['tender']
    if any([i.status != 'active' for i in tender.lots if i.id == request.context.lotID]):
        request.errors.add('body', 'data', 'Can add complaint only in active lot status')
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_award_complaint_update_only_for_active_lots(request):
    tender = request.validated['tender']
    if any([i.status != 'active' for i in tender.lots if i.id == request.validated['award'].lotID]):
        request.errors.add('body', 'data', 'Can update complaint only in active lot status')
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_add_complaint_not_in_complaint_period(request):
    if request.context.complaintPeriod and \
       (request.context.complaintPeriod.startDate and request.context.complaintPeriod.startDate > get_now() or
            request.context.complaintPeriod.endDate and request.context.complaintPeriod.endDate < get_now()):
        request.errors.add('body', 'data', 'Can add complaint only in complaintPeriod')
        request.errors.status = 403
        raise error_handler(request.errors)

# award complaint document
def validate_award_complaint_document_operation_not_in_allowed_status(request):
    if request.validated['tender_status'] not in ['active.qualification', 'active.awarded']:
        request.errors.add('body', 'data', 'Can\'t {} document in current ({}) tender status'.format('add' if request.method == 'POST' else 'update', request.validated['tender_status']))
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_award_complaint_document_operation_only_for_active_lots(request):
    if any([i.status != 'active' for i in request.validated['tender'].lots if i.id == request.validated['award'].lotID]):
        request.errors.add('body', 'data', 'Can {} document only in active lot status'.format('add' if request.method == 'POST' else 'update'))
        request.errors.status = 403
        raise error_handler(request.errors)

# contract
def validate_update_contract_only_for_active_lots(request):
    tender = request.validated['tender']
    if any([i.status != 'active' for i in tender.lots if i.id in [a.lotID for a in tender.awards if a.id == request.context.awardID]]):
        request.errors.add('body', 'data', 'Can update contract only in active lot status')
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_update_contract_value(request):
    tender = request.validated['tender']
    data = request.validated['data']
    if data['value']:
        for ro_attr in ('valueAddedTaxIncluded', 'currency'):
            if data['value'][ro_attr] != getattr(request.context.value, ro_attr):
                request.errors.add('body', 'data', 'Can\'t update {} for contract value'.format(ro_attr))
                request.errors.status = 403
                raise error_handler(request.errors)
        award = [a for a in tender.awards if a.id == request.context.awardID][0]
        if data['value']['amount'] > award.value.amount:
            request.errors.add('body', 'data', 'Value amount should be less or equal to awarded amount ({})'.format(award.value.amount))
            request.errors.status = 403
            raise error_handler(request.errors)
