# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import timedelta

from openprocurement.tender.belowthreshold.tests.base import (
    test_organization,
    now
)

from openprocurement.tender.openua.tests.base import (
    test_bids
)


# TenderBidResourceTest

def create_tender_biddder_invalid(self):
    response = self.app.post_json('/tenders/some_id/bids', {
        'data': {'tenderers': [test_organization], "value": {"amount": 500}}}, status=404)
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

    response = self.app.post_json(
        request_path, {'not_data': {}}, status=422)
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
        'data': {'selfEligible': True, 'selfQualified': True,
                 'tenderers': [{'identifier': 'invalid_value'}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'identifier': [
            u'Please use a mapping for this field or Identifier instance instead of unicode.']}, u'location': u'body',
            u'name': u'tenderers'}
    ])

    response = self.app.post_json(request_path, {
        'data': {'selfEligible': True, 'selfQualified': True,
                 'tenderers': [{'identifier': {}}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'contactPoint': [u'This field is required.'],
                           u'identifier': {u'scheme': [u'This field is required.'],
                                           u'id': [u'This field is required.']}, u'name': [u'This field is required.'],
                           u'address': [u'This field is required.']}], u'location': u'body', u'name': u'tenderers'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': [{'name': 'name',
                                                                         'identifier': {'uri': 'invalid_value'}}]}},
                                  status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'contactPoint': [u'This field is required.'],
                           u'identifier': {u'scheme': [u'This field is required.'], u'id': [u'This field is required.'],
                                           u'uri': [u'Not a well formed URL.']},
                           u'address': [u'This field is required.']}], u'location': u'body', u'name': u'tenderers'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': [test_organization]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'value'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': [test_organization],
                                                          "value": {"amount": 500, 'valueAddedTaxIncluded': False}}},
                                  status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [
            u'valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of tender'],
         u'location': u'body', u'name': u'value'}
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': [test_organization],
                                                          "value": {"amount": 500, 'currency': "USD"}}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'currency of bid should be identical to currency of value of tender'], u'location': u'body',
         u'name': u'value'},
    ])

    response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                          'tenderers': test_organization, "value": {"amount": 500}}},
                                  status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u"invalid literal for int() with base 10: 'contactPoint'", u'location': u'body',
         u'name': u'data'},
    ])


def create_tender_bidder(self):
    response = self.app.post_json('/tenders/{}/bids'.format(
        self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                   'tenderers': [test_organization], "value": {"amount": 500}}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    bid = response.json['data']
    self.assertEqual(bid['tenderers'][0]['name'], test_organization['name'])
    self.assertIn('id', bid)
    self.assertIn(bid['id'], response.headers['Location'])

    # set tender period in future
    data = deepcopy(self.initial_data)
    data["tenderPeriod"]["endDate"] = (now + timedelta(days=17)).isoformat()
    data["tenderPeriod"]["startDate"] = (now + timedelta(days=1)).isoformat()
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                   {'data': {'tenderPeriod': data["tenderPeriod"]}})
    self.assertEqual(response.status, '200 OK')

    response = self.app.post_json('/tenders/{}/bids'.format(
        self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                   'tenderers': [test_organization], "value": {"amount": 500}}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('Bid can be added only during the tendering period', response.json['errors'][0]["description"])

    self.set_status('complete')

    response = self.app.post_json('/tenders/{}/bids'.format(
        self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                   'tenderers': [test_organization], "value": {"amount": 500}}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add bid in current (complete) tender status")


def patch_tender_bidder(self):
    response = self.app.post_json('/tenders/{}/bids'.format(
        self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True, 'status': 'draft',
                                   'tenderers': [self.author_data], "value": {"amount": 500}}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    bid = response.json['data']
    bid_token = response.json['access']['token']

    response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token),
                                   {"data": {"value": {"amount": 600}}}, status=200)
    self.assertEqual(response.status, '200 OK')

    response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token),
                                   {"data": {'status': 'active'}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'value of bid should be less than value of tender'], u'location': u'body', u'name': u'value'}
    ])

    response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(
        self.tender_id, bid['id'], bid_token), {"data": {'status': 'active', "value": {"amount": 500}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    bid = response.json['data']

    response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(
        self.tender_id, bid['id'], bid_token), {"data": {'status': 'draft'}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Can\'t update bid to (draft) status', u'location': u'body', u'name': u'bid'}
    ])

    response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(
        self.tender_id, bid['id'], bid_token), {"data": {"value": {"amount": 400}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["value"]["amount"], 400)
    self.assertNotEqual(response.json['data']['date'], bid['date'])

    response = self.app.patch_json('/tenders/{}/bids/some_id'.format(self.tender_id),
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

    self.set_status('complete')

    response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, bid['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["value"]["amount"], 400)

    response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(
        self.tender_id, bid['id'], bid_token), {"data": {"value": {"amount": 400}}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update bid in current (complete) tender status")


def get_tender_bidder(self):
    response = self.app.post_json('/tenders/{}/bids'.format(
        self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                   'tenderers': [self.author_data], "value": {"amount": 500}}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    bid = response.json['data']
    bid_token = response.json['access']['token']

    response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, bid['id']), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't view bid in current (active.tendering) tender status")

    response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], bid)

    self.set_status('active.qualification')

    response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, bid['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    bid_data = response.json['data']
    # self.assertIn(u'participationUrl', bid_data)
    # bid_data.pop(u'participationUrl')
    self.assertEqual(bid_data, bid)

    response = self.app.get('/tenders/{}/bids/some_id'.format(self.tender_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'bid_id'}
    ])

    response = self.app.get('/tenders/some_id/bids/some_id', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'tender_id'}
    ])

    response = self.app.delete('/tenders/{}/bids/{}?acc_token={}'.format(
        self.tender_id, bid['id'], bid_token), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't delete bid in current (active.qualification) tender status")


def delete_tender_bidder(self):
    response = self.app.post_json('/tenders/{}/bids'.format(
        self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                   'tenderers': [self.author_data], "value": {"amount": 500}}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    bid = response.json['data']
    bid_token = response.json['access']['token']

    response = self.app.delete('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['id'], bid['id'])
    self.assertEqual(response.json['data']['status'], 'deleted')
    # deleted bid does not contain bid information
    self.assertFalse('value' in response.json['data'])
    self.assertFalse('tenderers' in response.json['data'])
    self.assertFalse('date' in response.json['data'])

    revisions = self.db.get(self.tender_id).get('revisions')
    self.assertTrue(any([i for i in revisions[-2][u'changes'] if i['op'] == u'remove' and i['path'] == u'/bids']))
    self.assertTrue(
        any([i for i in revisions[-1][u'changes'] if i['op'] == u'replace' and i['path'] == u'/bids/0/status']))

    response = self.app.delete('/tenders/{}/bids/some_id'.format(self.tender_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'bid_id'}
    ])

    response = self.app.delete('/tenders/some_id/bids/some_id', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'tender_id'}
    ])

    # finished tender does not show deleted bid info
    self.set_status('complete')
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']['bids']), 1)
    bid_data = response.json['data']['bids'][0]
    self.assertEqual(bid_data['id'], bid['id'])
    self.assertEqual(bid_data['status'], 'deleted')
    self.assertFalse('value' in bid_data)
    self.assertFalse('tenderers' in bid_data)
    self.assertFalse('date' in bid_data)


def deleted_bid_is_not_restorable(self):
    response = self.app.post_json('/tenders/{}/bids'.format(
        self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                   'tenderers': [test_organization], "value": {"amount": 500}}})
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
                                       'status': 'active',
                                   }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update bid in (deleted) status")

    response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], 'deleted')


def deleted_bid_do_not_locks_tender_in_state(self):
    bids = []
    bids_tokens = []
    for bid_amount in (400, 405):
        response = self.app.post_json('/tenders/{}/bids'.format(
            self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                       'tenderers': [self.author_data], "value": {"amount": bid_amount}}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bids.append(response.json['data'])
        bids_tokens.append(response.json['access']['token'])

    # delete first bid
    response = self.app.delete('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bids[0]['id'], bids_tokens[0]))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['id'], bids[0]['id'])
    self.assertEqual(response.json['data']['status'], 'deleted')

    # try to change tender state
    self.set_status('active.qualification')

    # check tender status
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['status'], 'active.qualification')

    # check bids
    response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, bids[0]['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['status'], 'deleted')
    response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, bids[1]['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['status'], 'active')


def get_tender_tenderers(self):
    response = self.app.post_json('/tenders/{}/bids'.format(
        self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                   'tenderers': [self.author_data], "value": {"amount": 500}}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    bid = response.json['data']

    response = self.app.get('/tenders/{}/bids'.format(self.tender_id), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't view bids in current (active.tendering) tender status")

    self.set_status('active.qualification')

    response = self.app.get('/tenders/{}/bids'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'][0], bid)

    response = self.app.get('/tenders/some_id/bids', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'tender_id'}
    ])


def bid_Administrator_change(self):
    response = self.app.post_json('/tenders/{}/bids'.format(
        self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                   'tenderers': [self.author_data], "value": {"amount": 500}}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    bid = response.json['data']
    self.app.authorization = ('Basic', ('administrator', ''))
    response = self.app.patch_json('/tenders/{}/bids/{}'.format(self.tender_id, bid['id']), {"data": {
        'tenderers': [{"identifier": {"id": "00000000"}}],
        "value": {"amount": 400}
    }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotEqual(response.json['data']["value"]["amount"], 400)
    self.assertEqual(response.json['data']["tenderers"][0]["identifier"]["id"], "00000000")


def draft1_bid(self):
    response = self.app.post_json('/tenders/{}/bids'.format(
        self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True, 'status': 'draft',
                                   'tenderers': [self.author_data], "value": {"amount": 500}}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')

    self.set_status('active.auction')
    self.set_status('active.auction', {"auctionPeriod": {"startDate": None}, 'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], 'unsuccessful')
    response = self.app.get('/tenders/{}/bids'.format(self.tender_id))
    self.assertEqual(response.json['data'], [])


def draft2_bids(self):
    response = self.app.post_json('/tenders/{}/bids'.format(
        self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True, 'status': 'draft',
                                   'tenderers': [self.author_data], "value": {"amount": 500}}})
    response = self.app.post_json('/tenders/{}/bids'.format(
        self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True, 'status': 'draft',
                                   'tenderers': [self.author_data], "value": {"amount": 500}}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')

    self.set_status('active.auction')
    self.set_status('active.auction', {"auctionPeriod": {"startDate": None}, 'status': 'active.tendering'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], 'unsuccessful')
    response = self.app.get('/tenders/{}/bids'.format(self.tender_id))
    self.assertEqual(response.json['data'], [])


def bids_invalidation_on_tender_change(self):
    bids_access = {}

    # submit bids
    for data in test_bids:
        response = self.app.post_json('/tenders/{}/bids'.format(
            self.tender_id), {'data': data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bids_access[response.json['data']['id']] = response.json['access']['token']

    # check initial status
    for bid_id, token in bids_access.items():
        response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid_id, token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active')

    # update tender. we can set value that is less than a value in bids as
    # they will be invalidated by this request
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
        self.tender_id, self.tender_token), {"data": {"value": {'amount': 300.0}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']["value"]["amount"], 300)

    # check bids status
    for bid_id, token in bids_access.items():
        response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid_id, token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'invalid')

    # check that tender status change does not invalidate bids
    # submit one more bid. check for invalid value first
    response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': test_bids[0]}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'value of bid should be less than value of tender'], u'location': u'body', u'name': u'value'}
    ])
    # and submit valid bid
    data = deepcopy(test_bids[0])
    data['value']['amount'] = 299
    response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': data})
    self.assertEqual(response.status, '201 Created')
    valid_bid_id = response.json['data']['id']

    # change tender status
    self.set_status('active.qualification')

    # check tender status
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['status'], 'active.qualification')
    # tender should display all bids
    self.assertEqual(len(response.json['data']['bids']), 3)
    # invalidated bids should show only 'id' and 'status' fields
    for bid in response.json['data']['bids']:
        if bid['status'] == 'invalid':
            self.assertTrue('id' in bid)
            self.assertFalse('value' in bid)
            self.assertFalse('tenderers' in bid)
            self.assertFalse('date' in bid)

    # invalidated bids stay invalidated
    for bid_id, token in bids_access.items():
        response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, bid_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'invalid')
        # invalidated bids displays only 'id' and 'status' fields
        self.assertFalse('value' in response.json['data'])
        self.assertFalse('tenderers' in response.json['data'])
        self.assertFalse('date' in response.json['data'])

    # and valid bid is not invalidated
    response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, valid_bid_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']['status'], 'active')
    # and displays all his data
    self.assertTrue('value' in response.json['data'])
    self.assertTrue('tenderers' in response.json['data'])
    self.assertTrue('date' in response.json['data'])

    # check bids availability on finished tender
    self.set_status('complete')
    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']['bids']), 3)
    for bid in response.json['data']['bids']:
        if bid['id'] in bids_access:  # previously invalidated bids
            self.assertEqual(bid['status'], 'invalid')
            self.assertFalse('value' in bid)
            self.assertFalse('tenderers' in bid)
            self.assertFalse('date' in bid)
        else:  # valid bid
            self.assertEqual(bid['status'], 'active')
            self.assertTrue('value' in bid)
            self.assertTrue('tenderers' in bid)
            self.assertTrue('date' in bid)


def bids_activation_on_tender_documents(self):
    bids_access = {}

    # submit bids
    for data in test_bids:
        response = self.app.post_json('/tenders/{}/bids'.format(
            self.tender_id), {'data': data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bids_access[response.json['data']['id']] = response.json['access']['token']
    # check initial status
    for bid_id, token in bids_access.items():
        response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid_id, token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active')

    response = self.app.post('/tenders/{}/documents?acc_token={}'.format(
        self.tender_id, self.tender_token), upload_files=[('file', u'укр.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')

    for bid_id, token in bids_access.items():
        response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid_id, token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'invalid')


# TenderBidResourceTest


def features_bidder(self):
    test_features_bids = [
        {
            # "status": "active",
            "parameters": [
                {
                    "code": i["code"],
                    "value": 0.1,
                }
                for i in self.initial_data['features']
            ],
            "tenderers": [
                test_organization
            ],
            "value": {
                "amount": 469,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            },
            'selfEligible': True, 'selfQualified': True,
        },
        {
            "status": "active",
            "parameters": [
                {
                    "code": i["code"],
                    "value": 0.15,
                }
                for i in self.initial_data['features']
            ],
            "tenderers": [
                test_organization
            ],
            "value": {
                "amount": 479,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            },
            'selfEligible': True, 'selfQualified': True,
        }
    ]
    for i in test_features_bids:
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': i})
        i['status'] = "active"
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bid = response.json['data']
        bid.pop(u'date')
        bid.pop(u'id')
        self.assertEqual(bid, i)


def features_bidder_invalid(self):
    data = {
        "tenderers": [
            test_organization
        ],
        "value": {
            "amount": 469,
            "currency": "UAH",
            "valueAddedTaxIncluded": True
        },
        'selfEligible': True, 'selfQualified': True,
    }
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


# TenderBidDocumentResourceTest


def create_tender_bidder_document(self):
    response = self.app.post('/tenders/{}/bids/{}/documents?acc_token={}'.format(
        self.tender_id, self.bid_id, self.bid_token), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual('name.doc', response.json["data"]["title"])
    key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

    response = self.app.get('/tenders/{}/bids/{}/documents'.format(self.tender_id, self.bid_id), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't view bid documents in current (active.tendering) tender status")

    response = self.app.get('/tenders/{}/bids/{}/documents?acc_token={}'.format(self.tender_id, self.bid_id, self.bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual('name.doc', response.json["data"][0]["title"])

    response = self.app.get('/tenders/{}/bids/{}/documents?all=true&acc_token={}'.format(self.tender_id, self.bid_id, self.bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual('name.doc', response.json["data"][0]["title"])

    response = self.app.get('/tenders/{}/bids/{}/documents/{}?download=some_id&acc_token={}'.format(
        self.tender_id, self.bid_id, doc_id, self.bid_token), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
    ])

    response = self.app.get('/tenders/{}/bids/{}/documents/{}?{}'.format(
        self.tender_id, self.bid_id, doc_id, key), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) tender status")

    if self.docservice:
        response = self.app.get('/tenders/{}/bids/{}/documents/{}?download={}&acc_token={}'.format(
            self.tender_id, self.bid_id, doc_id, key, self.bid_token))
        self.assertEqual(response.status, '302 Moved Temporarily')
        self.assertIn('http://localhost/get/', response.location)
        self.assertIn('Signature=', response.location)
        self.assertIn('KeyID=', response.location)
        self.assertIn('Expires=', response.location)
    else:
        response = self.app.get('/tenders/{}/bids/{}/documents/{}?download={}&acc_token={}'.format(
            self.tender_id, self.bid_id, doc_id, key, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 7)
        self.assertEqual(response.body, 'content')

    response = self.app.get('/tenders/{}/bids/{}/documents/{}'.format(
        self.tender_id, self.bid_id, doc_id), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) tender status")

    response = self.app.get('/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.tender_id, self.bid_id, doc_id, self.bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('name.doc', response.json["data"]["title"])

    self.set_status('active.awarded')

    response = self.app.post('/tenders/{}/bids/{}/documents?acc_token={}'.format(
        self.tender_id, self.bid_id, self.bid_token), upload_files=[('file', 'name.doc', 'content')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add document because award of bid is not in pending or active state")


def put_tender_bidder_document(self):
    response = self.app.post('/tenders/{}/bids/{}/documents?acc_token={}'.format(
        self.tender_id, self.bid_id, self.bid_token), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.put('/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(self.tender_id, self.bid_id, doc_id, self.bid_token),
                            status=404,
                            upload_files=[('invalid_name', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'body', u'name': u'file'}
    ])

    response = self.app.put('/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.tender_id, self.bid_id, doc_id, self.bid_token), upload_files=[('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

    if self.docservice:
        response = self.app.get('/tenders/{}/bids/{}/documents/{}?download={}&acc_token={}'.format(
            self.tender_id, self.bid_id, doc_id, key, self.bid_token))
        self.assertEqual(response.status, '302 Moved Temporarily')
        self.assertIn('http://localhost/get/', response.location)
        self.assertIn('Signature=', response.location)
        self.assertIn('KeyID=', response.location)
        self.assertIn('Expires=', response.location)
    else:
        response = self.app.get('/tenders/{}/bids/{}/documents/{}?download={}&acc_token={}'.format(
            self.tender_id, self.bid_id, doc_id, key, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content2')

    response = self.app.get('/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.tender_id, self.bid_id, doc_id, self.bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('name.doc', response.json["data"]["title"])

    response = self.app.put('/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.tender_id, self.bid_id, doc_id, self.bid_token), 'content3', content_type='application/msword')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

    if self.docservice:
        response = self.app.get('/tenders/{}/bids/{}/documents/{}?download={}&acc_token={}'.format(
            self.tender_id, self.bid_id, doc_id, key, self.bid_token))
        self.assertEqual(response.status, '302 Moved Temporarily')
        self.assertIn('http://localhost/get/', response.location)
        self.assertIn('Signature=', response.location)
        self.assertIn('KeyID=', response.location)
        self.assertIn('Expires=', response.location)
    else:
        response = self.app.get('/tenders/{}/bids/{}/documents/{}?download={}&acc_token={}'.format(
            self.tender_id, self.bid_id, doc_id, key, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content3')

    self.set_status('active.awarded')

    response = self.app.put('/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.tender_id, self.bid_id, doc_id, self.bid_token), upload_files=[('file', 'name.doc', 'content3')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document because award of bid is not in pending or active state")


def patch_tender_bidder_document(self):
    response = self.app.post('/tenders/{}/bids/{}/documents?acc_token={}'.format(
        self.tender_id, self.bid_id, self.bid_token), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.patch_json('/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(self.tender_id, self.bid_id, doc_id, self.bid_token), {"data": {
        "documentOf": "lot"
    }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'relatedItem'},
    ])

    response = self.app.patch_json('/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(self.tender_id, self.bid_id, doc_id, self.bid_token), {"data": {
        "documentOf": "lot",
        "relatedItem": '0' * 32
    }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'relatedItem should be one of lots'], u'location': u'body', u'name': u'relatedItem'}
    ])

    response = self.app.patch_json('/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(self.tender_id, self.bid_id, doc_id, self.bid_token), {"data": {"description": "document description"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get('/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.tender_id, self.bid_id, doc_id, self.bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('document description', response.json["data"]["description"])

    self.set_status('active.awarded')

    response = self.app.patch_json('/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.tender_id, self.bid_id, doc_id, self.bid_token), {"data": {"description": "document description"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document because award of bid is not in pending or active state")


def create_tender_bidder_document_nopending(self):
    response = self.app.post_json('/tenders/{}/bids'.format(
        self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                   'tenderers': [self.author_data], "value": {"amount": 500}}})
    bid = response.json['data']
    bid_id = bid['id']
    bid_token = response.json['access']['token']

    response = self.app.post('/tenders/{}/bids/{}/documents?acc_token={}'.format(
        self.tender_id, bid_id, bid_token), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    self.set_status('active.qualification')

    response = self.app.patch_json('/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.tender_id, bid_id, doc_id, bid_token), {"data": {"description": "document description"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document because award of bid is not in pending or active state")

    response = self.app.put('/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.tender_id, bid_id, doc_id, bid_token), 'content3', content_type='application/msword', status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document because award of bid is not in pending or active state")

    response = self.app.post('/tenders/{}/bids/{}/documents?acc_token={}'.format(
        self.tender_id, bid_id, bid_token), upload_files=[('file', 'name.doc', 'content')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add document because award of bid is not in pending or active state")


# TenderBidDocumentWithDSResourceTest


def create_tender_bidder_document_json(self):
    response = self.app.post_json('/tenders/{}/bids/{}/documents?acc_token={}'.format(self.tender_id, self.bid_id, self.bid_token),
        {'data': {
            'title': 'name.doc',
            'url': self.generate_docservice_url(),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual('name.doc', response.json["data"]["title"])
    key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

    response = self.app.get('/tenders/{}/bids/{}/documents'.format(self.tender_id, self.bid_id), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't view bid documents in current (active.tendering) tender status")

    response = self.app.get('/tenders/{}/bids/{}/documents?acc_token={}'.format(self.tender_id, self.bid_id, self.bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual('name.doc', response.json["data"][0]["title"])

    response = self.app.get('/tenders/{}/bids/{}/documents?all=true&acc_token={}'.format(self.tender_id, self.bid_id, self.bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual('name.doc', response.json["data"][0]["title"])

    response = self.app.get('/tenders/{}/bids/{}/documents/{}?download=some_id&acc_token={}'.format(
        self.tender_id, self.bid_id, doc_id, self.bid_token), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
    ])

    response = self.app.get('/tenders/{}/bids/{}/documents/{}?download={}'.format(
        self.tender_id, self.bid_id, doc_id, key), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) tender status")

    response = self.app.get('/tenders/{}/bids/{}/documents/{}?download={}&acc_token={}'.format(
        self.tender_id, self.bid_id, doc_id, key, self.bid_token))
    self.assertEqual(response.status, '302 Moved Temporarily')
    self.assertIn('http://localhost/get/', response.location)
    self.assertIn('Signature=', response.location)
    self.assertIn('KeyID=', response.location)
    self.assertIn('Expires=', response.location)

    response = self.app.get('/tenders/{}/bids/{}/documents/{}'.format(
        self.tender_id, self.bid_id, doc_id), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) tender status")

    response = self.app.get('/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.tender_id, self.bid_id, doc_id, self.bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('name.doc', response.json["data"]["title"])

    response = self.app.post_json('/tenders/{}/bids/{}/documents?acc_token={}'.format(self.tender_id, self.bid_id, self.bid_token),
        {'data': {
            'title': 'name.doc',
            'url': self.generate_docservice_url(),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn(response.json["data"]['id'], response.headers['Location'])
    self.assertEqual('name.doc', response.json["data"]["title"])

    self.set_status('active.awarded')

    response = self.app.post_json('/tenders/{}/bids/{}/documents?acc_token={}'.format(self.tender_id, self.bid_id, self.bid_token),
        {'data': {
            'title': 'name.doc',
            'url': self.generate_docservice_url(),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add document because award of bid is not in pending or active state")

    response = self.app.get('/tenders/{}/bids/{}/documents/{}'.format(self.tender_id, self.bid_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertIn('http://localhost/get/', response.json['data']['url'])
    self.assertIn('Signature=', response.json['data']['url'])
    self.assertIn('KeyID=', response.json['data']['url'])
    self.assertNotIn('Expires=', response.json['data']['url'])

    response = self.app.get('/tenders/{}/bids/{}/documents/{}?download={}&acc_token={}'.format(
        self.tender_id, self.bid_id, doc_id, key, self.bid_token))
    self.assertIn('http://localhost/get/', response.location)
    self.assertIn('Signature=', response.location)
    self.assertIn('KeyID=', response.location)
    self.assertIn('Expires=', response.location)


def put_tender_bidder_document_json(self):
    response = self.app.post_json('/tenders/{}/bids/{}/documents?acc_token={}'.format(self.tender_id, self.bid_id, self.bid_token),
        {'data': {
            'title': 'name.doc',
            'url': self.generate_docservice_url(),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.put_json('/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(self.tender_id, self.bid_id, doc_id, self.bid_token),
        {'data': {
            'title': 'name.doc',
            'url': self.generate_docservice_url(),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/tenders/{}/bids/{}/documents/{}?{}&acc_token={}'.format(
        self.tender_id, self.bid_id, doc_id, key, self.bid_token))
    self.assertEqual(response.status, '302 Moved Temporarily')
    self.assertIn('http://localhost/get/', response.location)
    self.assertIn('Signature=', response.location)
    self.assertIn('KeyID=', response.location)
    self.assertIn('Expires=', response.location)

    response = self.app.get('/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(
        self.tender_id, self.bid_id, doc_id, self.bid_token))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('name.doc', response.json["data"]["title"])

    response = self.app.put_json('/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(self.tender_id, self.bid_id, doc_id, self.bid_token),
        {'data': {
            'title': 'name.doc',
            'url': self.generate_docservice_url(),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/tenders/{}/bids/{}/documents/{}?{}&acc_token={}'.format(
        self.tender_id, self.bid_id, doc_id, key, self.bid_token))
    self.assertEqual(response.status, '302 Moved Temporarily')
    self.assertIn('http://localhost/get/', response.location)
    self.assertIn('Signature=', response.location)
    self.assertIn('KeyID=', response.location)
    self.assertIn('Expires=', response.location)

    self.set_status('active.awarded')

    response = self.app.put_json('/tenders/{}/bids/{}/documents/{}?acc_token={}'.format(self.tender_id, self.bid_id, doc_id, self.bid_token),
        {'data': {
            'title': 'name.doc',
            'url': self.generate_docservice_url(),
            'hash': 'md5:' + '0' * 32,
            'format': 'application/msword',
        }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document because award of bid is not in pending or active state")
