# -*- coding: utf-8 -*-
from datetime import timedelta
from iso8601 import parse_date
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
    ])

    response = self.app.post_json(request_path, {'data': {'invalid_field': 'invalid_value'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Rogue field', u'location': u'body', u'name': u'invalid_field'}
    ])

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
    self.assertEqual(response.json['data']['minValue']['amount'], 0)
    self.assertEqual(response.json['data']['minValue']['currency'], 'UAH')


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

    response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token), {'data': self.test_lots_data[0]})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    lot = response.json['data']

    response = self.app.get(request_path)
    self.assertEqual(len(response.json['data']['lots']), 3)
    self.assertEqual(response.json['data']['minValue']['amount'], sum([i['minValue']['amount'] for i in response.json['data']['lots']]))

    response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], lot)

    response = self.app.get(request_path)
    self.assertEqual(len(response.json['data']['lots']), 2)
    self.assertEqual(response.json['data']['minValue']['amount'], sum([i['minValue']['amount'] for i in response.json['data']['lots']]))


# TenderLotBidResourceTest

def create_tender_bid_invalid(self):
    request_path = '/tenders/{}/bids'.format(self.tender_id)
    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': self.test_bids_data[0]['tenderers']}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'lotValues'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [{"value": self.test_bids_data[0]['value']}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'relatedLot': [u'This field is required.']}], u'location': u'body', u'name': u'lotValues'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [{"value": self.test_bids_data[0]['value'], 'relatedLot': "0" * 32}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'relatedLot': [u'relatedLot should be one of lots']}], u'location': u'body', u'name': u'lotValues'}
    ])

    # comment this test while minValue = 0
    # response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [{"value": {
    #     'yearlyPayments': 0.9,
    #     'annualCostsReduction': 15.5,
    #     'contractDuration': 10}, 'relatedLot': self.initial_lots[0]['id']}]}}, status=422)
    # self.assertEqual(response.status, '422 Unprocessable Entity')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertEqual(response.json['status'], 'error')
    # self.assertEqual(response.json['errors'], [
    #     {u'description': [{u'value': [u'value of bid should be greater than minValue of lot']}], u'location': u'body', u'name': u'lotValues'}
    # ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [{"value": {
        'yearlyPayments': 0.9,
        'annualCostsReduction': 751.5,
        'contractDuration': 10,
        'valueAddedTaxIncluded': False}, 'relatedLot': self.initial_lots[0]['id']}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'value': [u'valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of minValue of lot']}], u'location': u'body', u'name': u'lotValues'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [{"value": {
        'yearlyPayments': 0.9,
        'annualCostsReduction': 751.5,
        'contractDuration': 10,
        'currency': "USD"}, 'relatedLot': self.initial_lots[0]['id']}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'value': [u'currency of bid should be identical to currency of minValue of lot']}], u'location': u'body', u'name': u'lotValues'},
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': self.test_bids_data[0]['tenderers'], "value": self.test_bids_data[0]['value'], 'lotValues': [{"value": self.test_bids_data[0]['value'], 'relatedLot': self.initial_lots[0]['id']}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'value should be posted for each lot of bid'], u'location': u'body', u'name': u'value'}
    ])


def patch_tender_bid(self):
    lot_id = self.initial_lots[0]['id']
    response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': self.test_bids_data[0]["tenderers"], 'lotValues': [{"value": self.test_bids_data[0]['value'], 'relatedLot': lot_id}]}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    bid = response.json['data']
    bid_token = response.json['access']['token']
    lot = bid['lotValues'][0]

    response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token), {"data": {'tenderers': [{"name": u"Державне управління управлінням справами"}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['lotValues'][0]['date'], lot['date'])
    self.assertNotEqual(response.json['data']['tenderers'][0]['name'], bid['tenderers'][0]['name'])

    response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token), {"data": {'lotValues': [{"value": {
        'yearlyPayments': 0.9,
        'annualCostsReduction': 760.5,
        'contractDuration': 10}, 'relatedLot': lot_id}], 'tenderers': self.test_bids_data[0]["tenderers"]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertAlmostEqual(parse_date(response.json['data']['lotValues'][0]['date']), parse_date(lot['date']), delta=timedelta(seconds=1))
    self.assertEqual(response.json['data']['tenderers'][0]['name'], bid['tenderers'][0]['name'])

    response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token), {"data": {'lotValues': [{"value": {
        'yearlyPayments': 0.9,
        'annualCostsReduction': 751.5,
        'contractDuration': 10}, 'relatedLot': lot_id}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['lotValues'][0]["value"]["amount"], 698.444)
    self.assertNotEqual(response.json['data']['lotValues'][0]['date'], lot['date'])

    self.time_shift('active.pre-qualification')
    self.check_chronograph()

    response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotIn('lotValues', response.json['data'])

    response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token), {"data": {'lotValues': [{"value": {"amount": 500}, 'relatedLot': lot_id}], 'status': 'active'}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update bid in current (unsuccessful) tender status")

# TenderLotFeatureBidResourceTest


def create_tender_feature_bid_invalid(self):
    request_path = '/tenders/{}/bids'.format(self.tender_id)
    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': self.test_bids_data[0]['tenderers']}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [{"value": self.test_bids_data[0]['value']}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'relatedLot': [u'This field is required.']}], u'location': u'body', u'name': u'lotValues'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [{"value": self.test_bids_data[0]['value'], 'relatedLot': "0" * 32}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'relatedLot': [u'relatedLot should be one of lots']}], u'location': u'body', u'name': u'lotValues'}
    ])

    # comment this test while minValue = 0
    # response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [{"value": {
    #     'yearlyPayments': 0.9,
    #     'annualCostsReduction': 15.5,
    #     'contractDuration': 10}, 'relatedLot': self.lot_id}]}}, status=422)
    # self.assertEqual(response.status, '422 Unprocessable Entity')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertEqual(response.json['status'], 'error')
    # self.assertEqual(response.json['errors'], [
    #     {u'description': [{u'value': [u'value of bid should be greater than minValue of lot']}], u'location': u'body', u'name': u'lotValues'}
    # ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [{"value": {
        'yearlyPayments': 0.9,
        'annualCostsReduction': 751.5,
        'contractDuration': 10,
        'valueAddedTaxIncluded': False}, 'relatedLot': self.lot_id}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'value': [u'valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of minValue of lot']}], u'location': u'body', u'name': u'lotValues'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [{"value": {
        'yearlyPayments': 0.9,
        'annualCostsReduction': 751.5,
        'contractDuration': 10,
        'currency': "USD"}, 'relatedLot': self.lot_id}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'value': [u'currency of bid should be identical to currency of minValue of lot']}], u'location': u'body', u'name': u'lotValues'},
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [{"value": self.test_bids_data[0]['value'], 'relatedLot': self.lot_id}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [{"value": self.test_bids_data[0]['value'], 'relatedLot': self.lot_id}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'All features parameters is required.'], u'location': u'body', u'name': u'parameters'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [{"value": self.test_bids_data[0]['value'], 'relatedLot': self.lot_id}], 'parameters': [{"code": "code_item", "value": 0.01}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'All features parameters is required.'], u'location': u'body', u'name': u'parameters'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [{"value": self.test_bids_data[0]['value'], 'relatedLot': self.lot_id}], 'parameters': [{"code": "code_invalid", "value": 0.01}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'code': [u'code should be one of feature code.']}], u'location': u'body', u'name': u'parameters'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': self.test_bids_data[0]['tenderers'], 'lotValues': [{"value": self.test_bids_data[0]['value'], 'relatedLot': self.lot_id}], 'parameters': [
        {"code": "code_item", "value": 0.01},
        {"code": "code_tenderer", "value": 0},
        {"code": "code_lot", "value": 0.01},
    ]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'value': [u'value should be one of feature value.']}], u'location': u'body', u'name': u'parameters'}
    ])


def create_tender_feature_bid(self):
    request_path = '/tenders/{}/bids'.format(self.tender_id)
    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': self.test_bids_data[0]["tenderers"], 'lotValues': [{"value": self.test_bids_data[0]['value'], 'relatedLot': self.lot_id}], 'parameters': [
        {"code": "code_item", "value": 0.01},
        {"code": "code_tenderer", "value": 0.01},
        {"code": "code_lot", "value": 0.01},
    ]}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    bid = response.json['data']
    self.assertEqual(bid['tenderers'][0]['name'], self.initial_data["procuringEntity"]['name'])
    self.assertIn('id', bid)
    self.assertIn(bid['id'], response.headers['Location'])

    self.time_shift('active.pre-qualification')
    self.check_chronograph()

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': self.test_bids_data[0]["tenderers"], 'lotValues': [{"value": self.test_bids_data[0]['value'], 'relatedLot': self.lot_id}], 'parameters': [
        {"code": "code_item", "value": 0.01},
        {"code": "code_tenderer", "value": 0.01},
        {"code": "code_lot", "value": 0.01},
    ]}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add bid in current (unsuccessful) tender status")
