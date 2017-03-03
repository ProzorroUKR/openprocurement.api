from openprocurement.api.validation import validate_data, validate_json_data
from openprocurement.api.utils import apply_data_patch

def validate_patch_tender_ua_data(request):
    data = validate_json_data(request)
    if request.context.status == 'draft':
        default_status = type(request.tender).fields['status'].default
        if data and data.get('status') != default_status:
            request.errors.add('body', 'data', 'Can\'t update tender in current (draft) status')
            request.errors.status = 403
            return
        request.validated['data'] = {'status': default_status}
        request.context.status = default_status
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

    return validate_data(request, type(request.tender), True, data)


