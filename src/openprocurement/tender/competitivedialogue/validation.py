from openprocurement.api.validation import (
    validate_data, validate_json_data
)
from openprocurement.api.utils import (
    apply_data_patch, update_logging_context, error_handler, raise_operation_error
)
from openprocurement.tender.competitivedialogue.models import STAGE2_STATUS
from openprocurement.tender.competitivedialogue.utils import (
    prepare_shortlistedFirms, prepare_author, prepare_bid_identifier
)


def validate_patch_tender_stage2_data(request):
    data = validate_json_data(request)
    if request.context.status == 'draft':
        default_statuses = ['active.tendering', STAGE2_STATUS]
        if data.get('status') not in default_statuses:
            raise_operation_error(request, 'Can\'t update tender in current ({0}) status'.format(data['status']))
        request.validated['data'] = {'status': data.get('status')}
        request.context.status = data.get('status')
        return
    if data:
        if 'items' in data:
            items = request.context.items
            cpv_group_lists = [i.classification.id[:3] for i in items]
            for item in data['items']:
                if 'classification' in item and 'id' in item['classification']:
                    cpv_group_lists.append(item['classification']['id'][:3])
            if len(set(cpv_group_lists)) != 1:
                request.errors.add('body', 'item', 'Can\'t change classification')
                request.errors.status = 403
                raise error_handler(request.errors)
        if 'enquiryPeriod' in data:
            if apply_data_patch(request.context.enquiryPeriod.serialize(), data['enquiryPeriod']):
                request.errors.add('body', 'item', 'Can\'t change enquiryPeriod')
                request.errors.status = 403
                raise error_handler(request.errors)
    if request.context.status == STAGE2_STATUS and data.get('status') == 'active.tendering':
        data = validate_data(request, type(request.tender), True, data)
        if data:  # if no error then add status to validate data
            request.context.status = 'active.tendering'
            data['status'] = 'active.tendering'
    else:
        data = validate_data(request, type(request.tender), True, data)

    return data


def get_item_by_id(tender, id):
    for item in tender['items']:
        if item['id'] == id:
            return item


def validate_author(request, shortlistedFirms, obj):
    """ Compare author key and key from shortlistedFirms """
    error_message = 'Author can\'t {} {}'.format('create' if request.method == 'POST' else 'patch',
                                                 obj.__class__.__name__.lower())
    firms_keys = prepare_shortlistedFirms(shortlistedFirms)
    author_key = prepare_author(obj)
    if obj.get('questionOf') == 'item':  # question can create on item
        if shortlistedFirms[0].get('lots'):
            item_id = author_key.split('_')[-1]
            item = get_item_by_id(request.validated['tender'], item_id)
            author_key = author_key.replace(author_key.split('_')[-1], item['relatedLot'])
        else:
            author_key = '_'.join(author_key.split('_')[:-1])
    for firm in firms_keys:
        if author_key in firm:  # if we found legal firm then check another complaint
            break
    else:  # we didn't find legal firm, then return error
        request.errors.add('body', 'author', error_message)
        request.errors.status = 403
        # return False
        raise error_handler(request.errors)
    return True


def validate_complaint_data_stage2(request):
    if not request.check_accreditation(request.tender.edit_accreditation):
        request.errors.add('procurementMethodType', 'accreditation', 'Broker Accreditation level does not permit complaint creation')
        request.errors.status = 403
        raise error_handler(request.errors)
    if request.tender.get('mode', None) is None and request.check_accreditation('t'):
        request.errors.add('procurementMethodType', 'mode', 'Broker Accreditation level does not permit complaint creation')
        request.errors.status = 403
        raise error_handler(request.errors)

    update_logging_context(request, {'complaint_id': '__new__'})
    data = validate_data(request, type(request.tender).complaints.model_class)
    if data:
        if validate_author(request, request.tender['shortlistedFirms'], request.validated['complaint']):
            return data  # validate is OK
        else:
            return None  # we catch errors
    return data


def validate_patch_complaint_data_stage2(request):
    model = type(request.tender).complaints.model_class
    data = validate_data(request, model, True)
    if data:
        if validate_author(request, request.tender['shortlistedFirms'], request.validated['complaint']):
            return data  # validate is OK
        else:
            return None  # we catch errors
    return data


def validate_post_question_data_stage2(request):
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
    data = validate_data(request, model)
    if data:
        if validate_author(request, request.tender['shortlistedFirms'], request.validated['question']):
            return data  # validate is OK
        else:
            return None  # we catch errors
    return data

# tender
def validate_credentials_generation(request):
    if request.validated['tender'].status != "draft.stage2":
        raise_operation_error(request, 'Can\'t generate credentials in current ({}) contract status'.format(request.validated['tender'].status))


def validate_tender_update(request):
    tender = request.context
    data = request.validated['data']
    if request.authenticated_role == 'tender_owner' and 'status' in data and \
            data['status'] not in ['active.pre-qualification.stand-still', 'active.stage2.waiting', tender.status]:
        raise_operation_error(request, 'Can\'t update tender status')

# bid
def validate_bid_status_update_not_to_pending_or_draft(request):
    if request.authenticated_role != 'Administrator':
        bid_status_to = request.validated['data'].get("status", request.context.status)
        if bid_status_to not in ['pending', 'draft']:
            request.errors.add('body', 'bid', 'Can\'t update bid to ({}) status'.format(bid_status_to))
            request.errors.status = 403
            raise error_handler(request.errors)


def validate_firm_to_create_bid(request):
    tender = request.validated['tender']
    bid = request.validated['bid']
    firm_keys = prepare_shortlistedFirms(tender.shortlistedFirms)
    bid_keys = prepare_bid_identifier(bid)
    if not (bid_keys <= firm_keys):
        raise_operation_error(request, 'Firm can\'t create bid')

# lot
def validate_lot_operation_for_stage2(request):
    operations = {"POST": "create", "PATCH": "update", "DELETE": "delete"}
    raise_operation_error(request, 'Can\'t {} lot for tender stage2'.format(operations.get(request.method)))
