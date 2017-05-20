# -*- coding: utf-8 -*-
from copy import deepcopy


# TenderBidResourceTest


def create_tender_bid_invalid(self):
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


def create_tender_bid(self):
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


def patch_tender_bid(self):
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


def features_bid_invalid(self):
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


def features_bid(self):
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


def get_tender_bidder_document(self):

    doc_id_by_type = {}
    # self.app.authorization = ('Basic', ('anon', ''))

    def document_is_unaccessible_for_others(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ('Basic', ('broker05', ''))
        response = self.app.get('/tenders/{}/bids/{}/{}'.format(self.tender_id, self.bid_id, resource), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        doc_id = doc_id_by_type[resource]['id']
        response = self.app.get('/tenders/{}/bids/{}/{}/{}'.format(self.tender_id, self.bid_id, resource, doc_id), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.app.authorization = orig_auth

    def document_is_unaccessible_for_tender_owner(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, resource, self.tender_token), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        doc_id = doc_id_by_type[resource]['id']
        response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, resource, doc_id, self.tender_token), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.app.authorization = orig_auth

    def all_documents_are_accessible_for_bid_owner(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ('Basic', ('broker', ''))
        for resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
            response = self.app.get('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, resource, self.bid_token))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(len(response.json['data']), 2)
            doc1 = response.json['data'][0]
            doc2 = response.json['data'][1]
            self.assertEqual(doc1['title'], 'name_{}.doc'.format(resource[:-1]))
            self.assertEqual(doc2['title'], 'name_{}_private.doc'.format(resource[:-1]))
            self.assertEqual(doc1['confidentiality'], u'public')
            self.assertEqual(doc2['confidentiality'], u'buyerOnly')
            self.assertIn('url', doc1)
            self.assertIn('url', doc2)
            doc_id = doc_id_by_type[resource]['id']
            response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, resource, doc_id, self.bid_token))
            self.assertEqual(response.status, '200 OK')
            self.assertIn('previousVersions', response.json['data'])
            doc = response.json['data']
            del doc['previousVersions']
            self.assertEqual(doc, doc1)
            doc_id = doc_id_by_type[resource+'private']['id']
            response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, resource, doc_id, self.bid_token))
            self.assertEqual(response.status, '200 OK')
            self.assertIn('previousVersions', response.json['data'])
            doc = response.json['data']
            del doc['previousVersions']
            self.assertEqual(doc, doc2)
        self.app.authorization = orig_auth

    def documents_are_accessible_for_tender_owner(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ('Basic', ('broker', ''))
        token = self.tender_token
        response = self.app.get('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, resource, token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 2)
        doc_id = doc_id_by_type[resource]['id']
        response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, resource, doc_id, token))
        self.assertIn('url', response.json['data'])
        self.assertEqual(response.status, '200 OK')
        doc_id = doc_id_by_type[resource+'private']['id']
        response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, resource, doc_id, token))
        self.assertEqual(response.status, '200 OK')
        self.assertIn('url', response.json['data'])
        self.app.authorization = orig_auth

    def public_documents_are_accessible_for_others(resource):
        orig_auth = self.app.authorization
        self.app.authorization = ('Basic', ('broker05', ''))

        response = self.app.get('/tenders/{}/bids/{}/{}'.format(self.tender_id, self.bid_id, resource))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 2)
        self.assertIn(doc_id_by_type[resource]['key'], response.json['data'][0]['url'])
        self.assertNotIn('url', response.json['data'][1])

        response = self.app.get('/tenders/{}/bids/{}/{}/{}'.format(self.tender_id, self.bid_id, resource,
                                                                   doc_id_by_type[resource]['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['title'], 'name_{}.doc'.format(resource[:-1]))
        self.assertEqual(response.json['data']['confidentiality'], u'public')
        self.assertEqual(response.json['data']['format'], u'application/msword')
        self.assertEqual(response.json['data']['language'], 'uk')

        response = self.app.get('/tenders/{}/bids/{}/{}/{}'.format(self.tender_id, self.bid_id, resource,
                                                                   doc_id_by_type[resource+'private']['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['confidentiality'], u'buyerOnly')
        self.assertNotIn('url', response.json['data'])

        self.app.authorization = orig_auth

    def all_public_documents_are_accessible_for_others():
        for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
            public_documents_are_accessible_for_others(doc_resource)

    # active.tendering
    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, self.bid_token), upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1].split('=')[-1]
        doc_id_by_type[doc_resource] = {'id': doc_id, 'key': key}

        # upload private document
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, self.bid_token), upload_files=[('file', 'name_{}_private.doc'.format(doc_resource[:-1]), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}_private.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1].split('=')[-1]
        doc_id_by_type[doc_resource+'private'] = {'id': doc_id, 'key': key}
        response = self.app.patch_json('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token), { "data": {
                'confidentiality': 'buyerOnly',
                'confidentialityRationale': 'Only our company sells badgers with pink hair.',
            }})
        self.assertEqual(response.status, '200 OK')

        document_is_unaccessible_for_others(doc_resource)
        document_is_unaccessible_for_tender_owner(doc_resource)

    all_documents_are_accessible_for_bid_owner(doc_resource)

    # switch to active.pre-qualification
    self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

    self.app.authorization = ('Basic', ('anon', ''))
    response = self.app.get('/tenders/{}/bids'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 2)
    self.assertEqual(set(response.json['data'][0].keys()), set(['id', 'status', 'documents', 'eligibilityDocuments', 'tenderers']))
    self.assertEqual(set(response.json['data'][1].keys()), set(['id', 'status', 'tenderers']))
    response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, self.bid_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(set(response.json['data'].keys()), set(['id', 'status', 'documents', 'eligibilityDocuments', 'tenderers']))

    for doc_resource in ['documents', 'eligibility_documents']:
        response = self.app.get('/tenders/{}/bids/{}/{}'.format(self.tender_id, self.bid_id, doc_resource))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 2)
        self.assertIn('url', response.json['data'][0])
        self.assertIn(doc_id_by_type[doc_resource]['key'], response.json['data'][0]['url'])
        self.assertNotIn('url', response.json['data'][1])

    for doc_resource in ['documents', 'eligibility_documents']:
        doc_id = doc_id_by_type[doc_resource]['id']
        response = self.app.get('/tenders/{}/bids/{}/{}/{}'.format(self.tender_id, self.bid_id, doc_resource, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['title'], u'name_{}.doc'.format(doc_resource[:-1]))
        self.assertEqual(response.json['data']['confidentiality'], u'public')
        self.assertEqual(response.json['data']['format'], u'application/msword')
        self.assertEqual(response.json['data']['language'], 'uk')

        doc_id = doc_id_by_type[doc_resource+'private']['id']
        response = self.app.get('/tenders/{}/bids/{}/{}/{}'.format(self.tender_id, self.bid_id, doc_resource, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['title'], u'name_{}_private.doc'.format(doc_resource[:-1]))
        self.assertEqual(response.json['data']['confidentiality'], u'buyerOnly')
        self.assertEqual(response.json['data']['format'], u'application/msword')
        self.assertEqual(response.json['data']['language'], 'uk')

    for doc_resource in ['financial_documents', 'qualification_documents']:
        document_is_unaccessible_for_others(doc_resource)
        document_is_unaccessible_for_tender_owner(doc_resource)

    for doc_resource in ['documents', 'eligibility_documents']:
        documents_are_accessible_for_tender_owner(doc_resource)
        public_documents_are_accessible_for_others(doc_resource)
    all_documents_are_accessible_for_bid_owner(doc_resource)


def create_tender_bidder_document(self):
    doc_id_by_type = {}
    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, self.bid_token), upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])


        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']

        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]
        doc_id_by_type[doc_resource] = {'id': doc_id, 'key': key}


    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.get('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, doc_resource, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id_by_type[doc_resource]['id'], response.json["data"][0]["id"])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"][0]["title"])

        response = self.app.get('/tenders/{}/bids/{}/{}?all=true&acc_token={}'.format(self.tender_id, self.bid_id, doc_resource, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id_by_type[doc_resource]['id'], response.json["data"][0]["id"])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"][0]["title"])

        doc_id = doc_id_by_type[doc_resource]['id']
        key = doc_id_by_type[doc_resource]['key']
        response = self.app.get('/tenders/{}/bids/{}/{}/{}?download=some_id&acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
        ])

        response = self.app.get('/tenders/{}/bids/{}/{}/{}?{}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, key), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) tender status")

        if self.docservice:
            response = self.app.get('/tenders/{}/bids/{}/{}/{}?{}&acc_token={}'.format(
                self.tender_id, self.bid_id, doc_resource, doc_id, key, self.bid_token))
            self.assertEqual(response.status, '302 Moved Temporarily')
            self.assertIn('http://localhost/get/', response.location)
            self.assertIn('Signature=', response.location)
            self.assertIn('KeyID=', response.location)
            self.assertIn('Expires=', response.location)
        else:
            response = self.app.get('/tenders/{}/bids/{}/{}/{}?{}&acc_token={}'.format(
                self.tender_id, self.bid_id, doc_resource, doc_id, key, self.bid_token))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/msword')
            self.assertEqual(response.content_length, 7)
            self.assertEqual(response.body, 'content')

        response = self.app.get('/tenders/{}/bids/{}/{}/{}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) tender status")

        response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])

    # switch to active.pre-qualification
    self.set_status('active.pre-qualification', {'status': 'active.tendering'})
    auth = self.app.authorization
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
    self.app.authorization = auth

    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, self.bid_token), upload_files=[('file', 'name.doc', 'content')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (active.pre-qualification) tender status")


def put_tender_bidder_document(self):
    doc_id_by_type = {}
    doc_id_by_type2 = {}
    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, self.bid_token), upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        doc_id_by_type[doc_resource] = {'id': doc_id, 'key': response.json["data"]["url"].split('?')[-1].split('=')[-1]}

        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid2_id, doc_resource, self.bid2_token), upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id_by_type2[doc_resource] = {'id': response.json["data"]['id'], 'key': response.json["data"]["url"].split('?')[-1].split('=')[-1]}

        response = self.app.put('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token), status=404,
                                upload_files=[('invalid_name', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.put('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token), upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

        response = self.app.get('/tenders/{}/bids/{}/{}/{}?download={}&acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, key, self.bid_token))
        if self.docservice:
            self.assertEqual(response.status, '302 Moved Temporarily')
            self.assertIn('http://localhost/get/', response.location)
            self.assertIn('Signature=', response.location)
            self.assertIn('KeyID=', response.location)
            self.assertIn('Expires=', response.location)
        else:
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/msword')
            self.assertEqual(response.content_length, 8)
            self.assertEqual(response.body, 'content2')

        response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name.doc', response.json["data"]["title"])

        response = self.app.put('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token), 'content3', content_type='application/msword')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

        response = self.app.get('/tenders/{}/bids/{}/{}/{}?download={}&acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, key, self.bid_token))
        if self.docservice:
            self.assertEqual(response.status, '302 Moved Temporarily')
            self.assertIn('http://localhost/get/', response.location)
            self.assertIn('Signature=', response.location)
            self.assertIn('KeyID=', response.location)
            self.assertIn('Expires=', response.location)
        else:
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/msword')
            self.assertEqual(response.content_length, 8)
            self.assertEqual(response.body, 'content3')

    # switch to active.pre-qualification
    self.set_status('active.pre-qualification', {'status': 'active.tendering'})
    auth = self.app.authorization
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
    self.app.authorization = auth

    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.put('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id_by_type[doc_resource]['id'], self.bid_token), upload_files=[('file', 'name.doc', 'content4')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (active.pre-qualification) tender status")


def patch_tender_bidder_document(self):
    doc_id_by_type = {}
    doc_id_by_type2 = {}
    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, self.bid_token), upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]
        doc_id_by_type[doc_resource] = {'id': doc_id, 'key': key}

        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid2_id, doc_resource, self.bid2_token), upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id_by_type2[doc_resource] = {'id': response.json["data"]['id'], 'key': response.json["data"]["url"].split('?')[-1]}

        # upload private document
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, self.bid_token), upload_files=[('file', 'name_{}_private.doc'.format(doc_resource[:-1]), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}_private.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]
        doc_id_by_type[doc_resource+'private'] = {'id': doc_id, 'key': key}
        response = self.app.patch_json('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token), { "data": {
                'confidentiality': 'buyerOnly',
                'confidentialityRationale': 'Only our company sells badgers with pink hair.',
            }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid2_id, doc_resource, self.bid2_token), upload_files=[('file', 'name_{}_private.doc'.format(doc_resource[:-1]), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}_private.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]
        doc_id_by_type2[doc_resource+'private'] = {'id': doc_id, 'key': key}
        response = self.app.patch_json('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid2_id, doc_resource, doc_id, self.bid2_token), { "data": {
                'confidentiality': 'buyerOnly',
                'confidentialityRationale': 'Only our company sells badgers with pink hair.',
            }})
        self.assertEqual(response.status, '200 OK')

    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        doc_id = doc_id_by_type[doc_resource]['id']
        response = self.app.patch_json('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token), {"data": {
            "documentOf": "lot"
        }}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'relatedItem'},
        ])

        response = self.app.patch_json('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token), {"data": {
            "documentOf": "lot",
            "relatedItem": '0' * 32
        }}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'relatedItem should be one of lots'], u'location': u'body', u'name': u'relatedItem'}
        ])

        response = self.app.patch_json('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token), {"data": {"description": "document description", 'language': 'en'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])

        response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('document description', response.json["data"]["description"])
        self.assertEqual('en', response.json["data"]["language"])

        # test confidentiality change
        doc_id = doc_id_by_type[doc_resource+'private']['id']
        response = self.app.patch_json('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token), { "data": {
                'confidentiality': 'public',
                'confidentialityRationale': '',
            }})
        self.assertEqual(response.status, '200 OK')
        response = self.app.patch_json('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token), { "data": {
                'confidentiality': 'buyerOnly',
                'confidentialityRationale': 'Only our company sells badgers with pink hair.',
            }})
        self.assertEqual(response.status, '200 OK')

    # switch to active.pre-qualification
    self.set_status('active.pre-qualification', {'status': 'active.tendering'})
    auth = self.app.authorization
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
    self.app.authorization = auth

    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.patch_json('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, doc_resource, doc_id_by_type[doc_resource]['id'], self.bid_token), {"data": {"description": "document description"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (active.pre-qualification) tender status")


def download_tender_bidder_document(self):
    doc_id_by_type = {}
    private_doc_id_by_type = {}
    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, self.bid_token), upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]
        private_doc_id_by_type[doc_resource] = {'id': response.json["data"]['id'], 'key': response.json["data"]["url"].split('?')[-1]}

        response = self.app.patch_json('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token), { "data": {
                'confidentiality': 'buyerOnly',
                'confidentialityRationale': 'Only our company sells badgers with pink hair.',
            }})

        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, self.bid_token), upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]
        doc_id_by_type[doc_resource] = {'id': response.json["data"]['id'], 'key': response.json["data"]["url"].split('?')[-1]}

        for container in private_doc_id_by_type, doc_id_by_type:
            response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}&{}'.format(
                self.tender_id, self.bid_id, doc_resource, container[doc_resource]['id'], self.bid_token, container[doc_resource]['key']))
            if self.docservice:
                self.assertEqual(response.status, '302 Moved Temporarily')
                self.assertIn('http://localhost/get/', response.location)
                self.assertIn('Signature=', response.location)
                self.assertIn('KeyID=', response.location)
                self.assertIn('Expires=', response.location)
            else:
                self.assertEqual(response.status, '200 OK')
                self.assertEqual(response.body, 'content')
                self.assertEqual(response.headers['Content-Disposition'],  'attachment; filename=name_{}.doc'.format(doc_resource[:-1]))
                self.assertEqual(response.headers['Content-Type'],  'application/msword; charset=UTF-8')

            response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}&{}'.format(
                self.tender_id, self.bid_id, doc_resource, container[doc_resource]['id'], self.tender_token, container[doc_resource]['key']), status=403)
            self.assertEqual(response.status, '403 Forbidden')
            self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) tender status")

            response = self.app.get('/tenders/{}/bids/{}/{}/{}?{}'.format(
                self.tender_id, self.bid_id, doc_resource, container[doc_resource]['id'], container[doc_resource]['key']), status=403)
            self.assertEqual(response.status, '403 Forbidden')
            self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) tender status")

    self.time_shift('active.pre-qualification')
    self.check_chronograph()

    def test_bids_documents_after_tendering_resource(self, doc_id_by_type, private_doc_id_by_type, status):
        for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
            for container in private_doc_id_by_type, doc_id_by_type:
                response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}&{}'.format(
                    self.tender_id, self.bid_id, doc_resource, container[doc_resource]['id'], self.bid_token, container[doc_resource]['key']))
                if self.docservice:
                    self.assertEqual(response.status, '302 Moved Temporarily')
                    self.assertIn('http://localhost/get/', response.location)
                    self.assertIn('Signature=', response.location)
                    self.assertIn('KeyID=', response.location)
                else:
                    self.assertEqual(response.status, '200 OK')
                    self.assertEqual(response.body, 'content')
                    self.assertEqual(response.headers['Content-Disposition'],  'attachment; filename=name_{}.doc'.format(doc_resource[:-1]))
                    self.assertEqual(response.headers['Content-Type'],  'application/msword; charset=UTF-8')

        for doc_resource in ['documents', 'eligibility_documents']:
            for container in private_doc_id_by_type, doc_id_by_type:
                response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}&{}'.format(
                    self.tender_id, self.bid_id, doc_resource, container[doc_resource]['id'], self.tender_token, container[doc_resource]['key']))
                if self.docservice:
                    self.assertEqual(response.status, '302 Moved Temporarily')
                    self.assertIn('http://localhost/get/', response.location)
                    self.assertIn('Signature=', response.location)
                    self.assertIn('KeyID=', response.location)
                else:
                    self.assertEqual(response.status, '200 OK')

        for doc_resource in ['financial_documents', 'qualification_documents']:
            for container in private_doc_id_by_type, doc_id_by_type:
                response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}&{}'.format(
                    self.tender_id, self.bid_id, doc_resource, container[doc_resource]['id'], self.tender_token, container[doc_resource]['key']), status=403)
                self.assertEqual(response.status, '403 Forbidden')
                self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current ({}) tender status".format(status))

        # for doc_resource in ['documents', 'eligibility_documents']:
            # for container in private_doc_id_by_type, doc_id_by_type:
                # response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}&{}'.format(
                    # self.tender_id, self.bid_id, doc_resource, container[doc_resource]['id'], self.tender_token, container[doc_resource]['key']))
                # self.assertEqual(response.status, '200 OK')

        for doc_resource in ['financial_documents', 'qualification_documents']:
            for container in private_doc_id_by_type, doc_id_by_type:
                response = self.app.get('/tenders/{}/bids/{}/{}/{}?{}'.format(
                    self.tender_id, self.bid_id, doc_resource, container[doc_resource]['id'], container[doc_resource]['key']), status=403)
                self.assertEqual(response.status, '403 Forbidden')
                self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current ({}) tender status".format(status))

    test_bids_documents_after_tendering_resource(self, doc_id_by_type, private_doc_id_by_type, 'active.pre-qualification')


def create_tender_bidder_document_nopending(self):
    response = self.app.post_json('/tenders/{}/bids'.format(
        self.tender_id), {'data': self.test_bids_data[0]})
    bid = response.json['data']
    token = response.json['access']['token']
    bid_id = bid['id']

    response = self.app.post('/tenders/{}/bids/{}/documents?acc_token={}'.format(
        self.tender_id, bid_id, token), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])


def patch_and_put_document_into_invalid_bid(self):
    doc_id_by_type = {}
    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, self.bid_token), upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]
        doc_id_by_type[doc_resource] = {'id': doc_id, 'key': key}

    # update tender. we can set value that is less than a value in bids as
    # they will be invalidated by this request
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token), {"data":
            {"minValue": {'amount': 10000.0}}
    })
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']["minValue"]["amount"], 10000)

    for doc_resource in ['documents', 'financial_documents', 'eligibility_documents', 'qualification_documents']:
        doc_id = doc_id_by_type[doc_resource]['id']
        response = self.app.patch_json('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token), { "data": {
                'confidentiality': 'buyerOnly',
                'confidentialityRationale': 'Only our company sells badgers with pink hair.',
            }}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document data for 'invalid' bid")
        response = self.app.put('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, doc_id, self.bid_token), 'updated', content_type='application/msword', status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in 'invalid' bid")
