from openprocurement.api.validation import validate_data, validate_json_data
from openprocurement.api.utils import apply_data_patch, update_logging_context
from openprocurement.tender.competitivedialogue.models import STAGE2_STATUS
from openprocurement.tender.competitivedialogue.utils import prepare_shortlistedFirms, prepare_author


def validate_patch_tender_stage2_data(request):
    data = validate_json_data(request)
    if request.context.status == 'draft':
        default_statuses = ['active.tendering', STAGE2_STATUS]
        if data.get('status') not in default_statuses:
            request.errors.add('body', 'data', 'Can\'t update tender in current ({0}) status'.format(data['status']))
            request.errors.status = 403
            return
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
                return None
        if 'enquiryPeriod' in data:
            if apply_data_patch(request.context.enquiryPeriod.serialize(), data['enquiryPeriod']):
                request.errors.add('body', 'item', 'Can\'t change enquiryPeriod')
                request.errors.status = 403
                return None
    if request.context.status == STAGE2_STATUS and data.get('status') == 'active.tendering':
        data = validate_data(request, type(request.tender), True, data)
        if data:  # if no error then add status to validate data
            request.context.status = 'active.tendering'
            data['status'] = 'active.tendering'
    else:
        data = validate_data(request, type(request.tender), True, data)

    return data


def validate_author(request, shortlistedFirms, obj):
    error_message = 'Author can\'t {} {}'.format('create' if request.method == 'POST' else 'patch',
                                                 obj.__class__.__name__.lower())
    firms_key = prepare_shortlistedFirms(shortlistedFirms)
    author_key = prepare_author(obj)
    for firm in firms_key:
        if author_key in firm:  # if we found legal firm then check another complaint
            break
    else:  # we didn't find legal firm, then return error
        request.errors.add('body', 'author', error_message)
        request.errors.status = 403
        return False
    return True

def validate_complaint_data_stage2(request):
    if not request.check_accreditation(request.tender.edit_accreditation):
        request.errors.add('procurementMethodType', 'accreditation', 'Broker Accreditation level does not permit complaint creation')
        request.errors.status = 403
        return
    if request.tender.get('mode', None) is None and request.check_accreditation('t'):
        request.errors.add('procurementMethodType', 'mode', 'Broker Accreditation level does not permit complaint creation')
        request.errors.status = 403
        return

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
        return
    if request.tender.get('mode', None) is None and request.check_accreditation('t'):
        request.errors.add('procurementMethodType', 'mode', 'Broker Accreditation level does not permit question creation')
        request.errors.status = 403
        return
    update_logging_context(request, {'question_id': '__new__'})
    model = type(request.tender).questions.model_class
    data = validate_data(request, model)
    if data:
        if validate_author(request, request.tender['shortlistedFirms'], request.validated['question']):
            return data  # validate is OK
        else:
            return None  # we catch errors
    return data

