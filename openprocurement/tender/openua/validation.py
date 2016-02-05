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
        if 'tenderPeriod' in data:
            data["auctionPeriod"] = {'startDate': None}
            if len(request.context.lots) > 0:
                lots = list(data['lots']) if 'lots' in data else []
                data['lots'] = []
                for index, lot in enumerate(request.context.lots):
                    lot_data = lots[index] if lots else {}

                    lot_data['auctionPeriod'] = {'startDate': None}
                    data['lots'].append(lot_data)

    return validate_data(request, request.tender.__class__, True, data)
