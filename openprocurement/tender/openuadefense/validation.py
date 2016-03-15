from openprocurement.api.validation import validate_data, validate_json_data


def validate_patch_tender_ua_data(request):
    data = validate_json_data(request)
    classification_id = request.context.items[0].classification.id
    if data:
        if 'items' in data:
            for item in data['items']:
                if 'classification' in item:
                    if item['classification'].get('id', '') != classification_id:
                        request.errors.add('body', 'item', 'Can\'t change classification')
                        request.errors.status = 403
                        return None
        if 'enquiryPeriod' in data:
            request.errors.add('body', 'item', 'Can\'t change enquiryPeriod')
            request.errors.status = 403
            return None

    return validate_data(request, request.tender.__class__, True, data)
