# -*- coding: utf-8 -*-
from copy import deepcopy


# TenderBidResourceTest


def create_tender_bidder_invalid(self):
    response = self.app.post_json('/tenders/some_id/bids', {
        'data': {'tenderers': [self.author_data], "value": {"amount": 500}}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'tender_id'}
    ])

    request_path = '/tenders/{}/bids'.format(self.tender_id)
    response = self.app.post(request_path, 'data', status=415)
    self.assertEqual(response.status, '415 Unsupported Media Type')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description':
             u"Content-Type header should be one of ['application/json']", u'location': u'header',
         u'name': u'Content-Type'}
    ])

    response = self.app.post(
        request_path, 'data', content_type='application/json', status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'No JSON object could be decoded',
         u'location': u'body', u'name': u'data'}
    ])

    response = self.app.post_json(request_path, 'data', status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Data not available',
         u'location': u'body', u'name': u'data'}
    ])

    response = self.app.post_json(request_path, {'not_data': {}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Data not available',
         u'location': u'body', u'name': u'data'}
    ])

    response = self.app.post_json(request_path, {'data': {
        'invalid_field': 'invalid_value'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Rogue field', u'location':
            u'body', u'name': u'invalid_field'}
    ])

    response = self.app.post_json(request_path, {
        'data': {'tenderers': [{'identifier': 'invalid_value'}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'identifier': [
            u'Please use a mapping for this field or Identifier instance instead of unicode.']}, u'location': u'body',
            u'name': u'tenderers'}
    ])

    response = self.app.post_json(request_path, {
        'data': {'tenderers': [{'identifier': {}}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'selfEligible'},
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'selfQualified'},
        {u'description': [
            {u'contactPoint': [u'This field is required.'],
             u'identifier': {u'scheme': [u'This field is required.'], u'id': [u'This field is required.']},
             u'name': [u'This field is required.'],
             u'address': [u'This field is required.']}
        ], u'location': u'body', u'name': u'tenderers'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': False, 'tenderers': [{
        'name': 'name', 'identifier': {'uri': 'invalid_value'}}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'Value must be one of [True].'], u'location': u'body', u'name': u'selfEligible'},
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'selfQualified'},
        {u'description': [{
            u'contactPoint': [u'This field is required.'],
            u'identifier': {u'scheme': [u'This field is required.'],
                            u'id': [u'This field is required.'],
                            u'uri': [u'Not a well formed URL.']},
            u'address': [u'This field is required.']}],
            u'location': u'body', u'name': u'tenderers'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': [self.author_data]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'value'}
    ])

    response = self.app.post_json(request_path, {'data': {
        'selfEligible': True, 'selfQualified': True,
        'tenderers': [self.author_data], 'value': {}}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'location': u'body', u'name': u'value',
         u'description': {u'contractDuration': [u'This field is required.'],
                          u'annualCostsReduction': [u'This field is required.'],
                          u'yearlyPayments': [u'This field is required.']}}
    ])

    response = self.app.post_json(request_path, {'data': {
        'selfEligible': True, 'selfQualified': True,
        'tenderers': [self.author_data], 'value': {'amount': 500}}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'location': u'body', u'name': u'value',
         u'description': {u'contractDuration': [u'This field is required.'],
                          u'annualCostsReduction': [u'This field is required.'],
                          u'yearlyPayments': [u'This field is required.']}}
    ])

    response = self.app.post_json(request_path, {'data': {
        'selfEligible': True, 'selfQualified': True, 'tenderers': [self.author_data],
        'value': {'contractDuration': 0}}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'location': u'body', u'name': u'value',
         u'description': {u'annualCostsReduction': [u'This field is required.'],
                          u'yearlyPayments': [u'This field is required.'],
                          u'contractDuration': [u'Int value should be greater than 1.']}}
    ])

    response = self.app.post_json(request_path, {'data': {
        'selfEligible': True, 'selfQualified': True, 'tenderers': [self.author_data],
        'value': {'contractDuration': 20}}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'location': u'body', u'name': u'value',
         u'description': {u'annualCostsReduction': [u'This field is required.'],
                          u'yearlyPayments': [u'This field is required.'],
                          u'contractDuration': [u'Int value should be less than 15.']}}
    ])

    response = self.app.post_json(request_path, {'data': {
        'selfEligible': True, 'selfQualified': True, 'tenderers': [self.author_data],
        'value': {'yearlyPayments': 0}}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'location': u'body', u'name': u'value',
         u'description': {u'contractDuration': [u'This field is required.'],
                          u'annualCostsReduction': [u'This field is required.'],
                          u'yearlyPayments': [u'Float value should be greater than 0.8.']}}
    ])

    response = self.app.post_json(request_path, {'data': {
        'selfEligible': True, 'selfQualified': True, 'tenderers': [self.author_data],
        'value': {'yearlyPayments': 1}}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'location': u'body', u'name': u'value',
         u'description': {u'contractDuration': [u'This field is required.'],
                          u'annualCostsReduction': [u'This field is required.'],
                          u'yearlyPayments': [u'Float value should be less than 0.9.']}}
    ])
    # create bid with given value.amount
    response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': {
        'selfEligible': True, 'selfQualified': True, 'tenderers': [self.author_data],
        'value': {'contractDuration': 6,
                  'annualCostsReduction': 300.6,
                  'yearlyPayments': 0.9,
                  'amount': 1000}}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'location': u'body', u'name': u'value',
         u'description': [u'value of bid should be greater than minValue of tender']}
    ])


def create_tender_bidder(self):
    response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                  {'data': self.test_bids_data[0]})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    bid = response.json['data']
    self.assertEqual(bid['tenderers'][0]['name'],
                     self.test_bids_data[0]['tenderers'][0]['name'])
    self.assertIn('id', bid)
    self.assertIn(bid['id'], response.headers['Location'])
    self.assertIn('value', bid)
    self.assertEqual(bid['value']['contractDuration'], 10)
    self.assertEqual(bid['value']['annualCostsReduction'], 751.5)
    self.assertEqual(bid['value']['yearlyPayments'], 0.9)
    self.assertEqual(bid['value']['amount'], 698.444)

    for status in ('active', 'unsuccessful', 'deleted', 'invalid'):
        data = deepcopy(self.test_bids_data[0])
        data.update({'status': status})
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': data}, status=403)
        self.assertEqual(response.status, '403 Forbidden')

    self.set_status('complete')

    response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': {
        'selfEligible': True, 'selfQualified': True, 'tenderers': [self.author_data],
        'value': {'contractDuration': 10,
                  'annualCostsReduction': 751.5,
                  'yearlyPayments': 0.9}}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add bid in current (complete) tender status")


def patch_tender_bidder(self):
    response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                  {'data': self.test_bids_data[0]})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    bid = response.json['data']
    bid_token = response.json['access']['token']

    response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token), {'data': {
        'value': {'contractDuration': 6,
                  'annualCostsReduction': 300.6,
                  'yearlyPayments': 0.9}
    }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'location': u'body', u'name': u'value',
         u'description': [u'value of bid should be greater than minValue of tender']}
    ])

    response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token),
                                   {"data": {'tenderers': [{"name": u"Державне управління управлінням справами"}]}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['date'], bid['date'])
    self.assertNotEqual(response.json['data']['tenderers'][0]['name'], bid['tenderers'][0]['name'])

    response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token),
                                   {"data": {"value": {"amount": 500}, 'tenderers': self.test_bids_data[0]['tenderers']}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['date'], bid['date'])
    self.assertEqual(response.json['data']['value'], bid['value'])
    self.assertEqual(response.json['data']['tenderers'][0]['name'], bid['tenderers'][0]['name'])
    self.assertNotEqual(response.json['data']['value']['amount'], 500)

    response = self.app.patch_json('/tenders/{}/bids/some_id?acc_token={}'.format(self.tender_id, bid_token),
                                   {"data": {"value": {"amount": 400}}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'bid_id'}
    ])

    response = self.app.patch_json('/tenders/some_id/bids/some_id', {"data": {"value": {"amount": 400}}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'tender_id'}
    ])

    for status in ('invalid', 'active', 'unsuccessful', 'deleted', 'draft'):
        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token),
                                       {'data': {'status': status}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update bid to ({}) status".format(status))

    response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token),
                                   {"data": {"value": {"amount": 400}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    self.set_status('complete')

    response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, bid['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotEqual(response.json['data']["value"]["amount"], 400)

    response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token),
                                   {"data": {"value": {"amount": 400}}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update bid in current (complete) tender status")


def deleted_bid_is_not_restorable(self):
    response = self.app.post_json('/tenders/{}/bids'.format(
        self.tender_id), {'data': self.test_bids_data[0]})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    bid = response.json['data']
    bid_token = response.json['access']['token']

    response = self.app.delete('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['id'], bid['id'])
    self.assertEqual(response.json['data']['status'], 'deleted')

    # try to restore deleted bid
    response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token),
                                   {"data": {
                                       'status': 'pending',
                                   }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update bid in (deleted) status")

    response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], 'deleted')


def bid_Administrator_change(self):
    response = self.app.post_json('/tenders/{}/bids'.format(
        self.tender_id), {'data': self.test_bids_data[0]})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    bid = response.json['data']

    self.app.authorization = ('Basic', ('administrator', ''))
    response = self.app.patch_json('/tenders/{}/bids/{}'.format(self.tender_id, bid['id']), {"data": {
        'selfEligible': True, 'selfQualified': True,
        'tenderers': [{"identifier": {"id": "00000000"}}],
        "value": {"amount": 400}
    }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotEqual(response.json['data']["value"]["amount"], 400)
    self.assertEqual(response.json['data']["tenderers"][0]["identifier"]["id"], "00000000")

    response = self.app.patch_json('/tenders/{}/bids/{}'.format(self.tender_id, bid['id']), {'data': {
        'value': {'annualCostsReduction': 300.6,
                  'contractDuration': 6,
                  'yearlyPayments': 0.9}}
    }, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {"location": "body", "name": "value",
         "description": ["value of bid should be greater than minValue of tender"]}
    ])


def bids_activation_on_tender_documents(self):
    bids_access = {}

    # submit bids
    for _ in range(2):
        response = self.app.post_json('/tenders/{}/bids'.format(
            self.tender_id), {'data': self.test_bids_data[0]})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bids_access[response.json['data']['id']] = response.json['access']['token']

    # check initial status
    for bid_id, token in bids_access.items():
        response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid_id, token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'pending')

    response = self.app.post('/tenders/{}/documents?acc_token={}'.format(
        self.tender_id, self.tender_token), upload_files=[('file', u'укр.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')

    for bid_id, token in bids_access.items():
        response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid_id, token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'invalid')

    # activate bids
    for bid_id, token in bids_access.items():
        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid_id, token),
                                       {'data': {'status': 'pending'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'pending')


# TenderBidFeaturesResourceTest


def features_bidder_invalid(self):
    data = deepcopy(self.test_bids_data[0])
    response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'parameters'}
    ])
    data["parameters"] = [
        {
            "code": "OCDS-123454-AIR-INTAKE",
            "value": 0.1,
        }
    ]
    response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'All features parameters is required.'], u'location': u'body', u'name': u'parameters'}
    ])
    data["parameters"].append({
        "code": "OCDS-123454-AIR-INTAKE",
        "value": 0.1,
    })
    response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'Parameter code should be uniq for all parameters'], u'location': u'body', u'name': u'parameters'}
    ])
    data["parameters"][1]["code"] = "OCDS-123454-YEARS"
    data["parameters"][1]["value"] = 0.2
    response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'value': [u'value should be one of feature value.']}], u'location': u'body', u'name': u'parameters'}
    ])


def features_bidder(self):
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data.update({
        "parameters": [
            {
                "code": i["code"],
                "value": 0.1,
            }
            for i in self.initial_data['features']
        ]
    })
    for i in [bid_data] * 2:
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': i})
        i['status'] = "pending"
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bid = response.json['data']
        bid.pop(u'date')
        bid.pop(u'id')
        self.assertEqual(set(bid), set(i))
