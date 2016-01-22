from openprocurement.api.validation import validate_data, validate_json_data

def validate_patch_tender_ua_data(request):
    data = validate_json_data(request)
    if 'tenderPeriod' in data:
        data["auctionPeriod"] = {'startDate': None}

    return validate_data(request, request.tender.__class__, True, data)
