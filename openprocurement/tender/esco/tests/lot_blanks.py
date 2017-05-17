# -*- coding: utf-8 -*-
# Tender Lot Resouce Test


def create_tender_lot_invalid(self):
    response = self.app.post_json('/tenders/some_id/lots', {'data': {'title': 'lot title', 'description': 'lot description'}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}
    ])

    request_path = '/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token)

    response = self.app.post(request_path, 'data', status=415)
    self.assertEqual(response.status, '415 Unsupported Media Type')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description':
            u"Content-Type header should be one of ['application/json']", u'location': u'header', u'name': u'Content-Type'}
    ])

    response = self.app.post(request_path, 'data', content_type='application/json', status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'No JSON object could be decoded', u'location': u'body', u'name': u'data'}
    ])

    response = self.app.post_json(request_path, 'data', status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Data not available', u'location': u'body', u'name': u'data'}
    ])

    response = self.app.post_json(request_path, {'not_data': {}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Data not available',u'location': u'body', u'name': u'data'}
    ])

    response = self.app.post_json(request_path, {'data': {}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'minimalStep'},
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'title'},
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'minValue'},
    ])

    response = self.app.post_json(request_path, {'data': {'invalid_field': 'invalid_value'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Rogue field', u'location': u'body', u'name': u'invalid_field'}
    ])

    response = self.app.post_json(request_path, {'data': {'minValue': 'invalid_value'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [
            u'Please use a mapping for this field or Value instance instead of unicode.'], u'location': u'body', u'name': u'minValue'}
    ])

    response = self.app.post_json(request_path, {'data': {
        'title': 'lot title',
        'description': 'lot description',
        'minValue': {'amount': '100.0'},
        'minimalStep': {'amount': '500.0'},
    }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'value should be less than minValue of lot'], u'location': u'body', u'name': u'minimalStep'}
    ])

    response = self.app.post_json(request_path, {'data': {
        'title': 'lot title',
        'description': 'lot description',
        'minValue': {'amount': '500.0'},
        'minimalStep': {'amount': '100.0', 'currency': "USD"}
    }})
    self.assertEqual(response.status, '201 Created')
    # but minimalStep currency stays unchanged
    response = self.app.get(request_path)
    self.assertEqual(response.content_type, 'application/json')
    lots = response.json['data']
    self.assertEqual(len(lots), 1)
    self.assertEqual(lots[0]['minimalStep']['currency'], "UAH")
    self.assertEqual(lots[0]['minimalStep']['amount'], 100)

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token), {"data": {"items": [{'relatedLot': '0' * 32}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'relatedLot': [u'relatedLot should be one of lots']}], u'location': u'body', u'name': u'items'}
    ])


def patch_tender_lot_minValue(self):
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token), {'data': self.test_lots_data[0]})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']

    response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token), {"data": {"minValue": {"amount": 300}}})
    self.assertEqual(response.status, '200 OK')
    self.assertIn('minValue', response.json['data'])
    self.assertEqual(response.json['data']['minValue']['amount'], 300)
    self.assertEqual(response.json['data']['minValue']['currency'], 'UAH')


def patch_tender_currency(self):
    # create lot
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token), {'data': self.test_lots_data[0]})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']
    self.assertEqual(lot['minValue']['currency'], "UAH")

    # update tender currency without mimimalStep currency change
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token), {"data": {"minValue": {"currency": "GBP"}}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'currency should be identical to currency of minValue of tender'],
         u'location': u'body', u'name': u'minimalStep'}
    ])

    # update tender currency
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token), {"data": {
        "minValue": {"currency": "GBP"},
        "minimalStep": {"currency": "GBP"}
    }})
    self.assertEqual(response.status, '200 OK')
    # log currency is updated too
    response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']
    self.assertEqual(lot['minValue']['currency'], "GBP")

    # try to update lot currency
    response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token), {"data": {"minValue": {"currency": "USD"}}})
    self.assertEqual(response.status, '200 OK')
    # but the value stays unchanged
    response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']
    self.assertEqual(lot['minValue']['currency'], "GBP")

    # try to update minimalStep currency
    response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token), {"data": {"minimalStep": {"currency": "USD"}}})
    self.assertEqual(response.status, '200 OK')
    # but the value stays unchanged
    response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']
    self.assertEqual(lot['minimalStep']['currency'], "GBP")

    # try to update lot minimalStep currency and lot value currency in single request
    response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token), {"data": {"minValue": {"currency": "USD"},
                                                                                                      "minimalStep": {"currency": "USD"}}})
    self.assertEqual(response.status, '200 OK')
    # but the value stays unchanged
    response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']
    self.assertEqual(lot['minValue']['currency'], "GBP")
    self.assertEqual(lot['minimalStep']['currency'], "GBP")


def patch_tender_vat(self):
    # set tender VAT
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token), {"data": {"minValue": {"valueAddedTaxIncluded": True}}})
    self.assertEqual(response.status, '200 OK')

    # create lot
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token), {'data': self.test_lots_data[0]})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']
    self.assertTrue(lot['minValue']['valueAddedTaxIncluded'])

    # update tender VAT
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token), {"data":
                                                                          {"minValue": {"valueAddedTaxIncluded": False},
                                                                           "minimalStep": {"valueAddedTaxIncluded": False}}
                                                                          })
    self.assertEqual(response.status, '200 OK')
    # log VAT is updated too
    response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']
    self.assertFalse(lot['minValue']['valueAddedTaxIncluded'])

    # try to update lot VAT
    response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token), {"data": {"minValue": {"valueAddedTaxIncluded": True}}})
    self.assertEqual(response.status, '200 OK')
    # but the value stays unchanged
    response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']
    self.assertFalse(lot['minValue']['valueAddedTaxIncluded'])

    # try to update minimalStep VAT
    response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token), {"data": {"minimalStep": {"valueAddedTaxIncluded": True}}})
    self.assertEqual(response.status, '200 OK')
    # but the value stays unchanged
    response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']
    self.assertFalse(lot['minimalStep']['valueAddedTaxIncluded'])

    # try to update minimalStep VAT and value VAT in single request
    response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token), {"data": {"minValue": {"valueAddedTaxIncluded": True},
                                                                                                      "minimalStep": {"valueAddedTaxIncluded": True}}})
    self.assertEqual(response.status, '200 OK')
    # but the value stays unchanged
    response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']
    self.assertFalse(lot['minValue']['valueAddedTaxIncluded'])
    self.assertEqual(lot['minimalStep']['valueAddedTaxIncluded'], lot['minValue']['valueAddedTaxIncluded'])


def get_tender_lot(self):
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(
        self.tender_id, self.tender_token), {'data': self.test_lots_data[0]})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']

    response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(set(response.json['data']), set(
        [u'status', u'date', u'description', u'title', u'minimalStep', u'auctionPeriod', u'minValue', u'id']))

    self.set_status('active.qualification')

    response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    lot.pop('auctionPeriod')
    self.assertEqual(response.json['data'], lot)

    response = self.app.get('/tenders/{}/lots/some_id'.format(self.tender_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'lot_id'}
    ])

    response = self.app.get('/tenders/some_id/lots/some_id', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'tender_id'}
    ])


def get_tender_lots(self):
    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(
        self.tender_id, self.tender_token), {'data': self.test_lots_data[0]})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']

    response = self.app.get('/tenders/{}/lots'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(set(response.json['data'][0]), set(
        [u'status', u'description', u'date', u'title', u'minimalStep', u'auctionPeriod', u'minValue', u'id']))

    self.set_status('active.qualification')

    response = self.app.get('/tenders/{}/lots'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    lot.pop('auctionPeriod')
    self.assertEqual(response.json['data'][0], lot)

    response = self.app.get('/tenders/some_id/lots', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'tender_id'}
    ])


# Tender Lot Feature Resource Test


def tender_min_value(self):
    request_path = '/tenders/{}'.format(self.tender_id)
    response = self.app.get(request_path)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['minValue']['amount'], sum([i['minValue']['amount'] for i in self.initial_lots]))
    self.assertEqual(response.json['data']['minimalStep']['amount'], min([i['minimalStep']['amount'] for i in self.initial_lots]))
