from openprocurement.api.validation import validate_data, validate_json_data
from openprocurement.api.utils import apply_data_patch
from openprocurement.tender.competitivedialogue.models import STAGE2_STATUS


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
