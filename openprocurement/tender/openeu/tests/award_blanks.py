# -*- coding: utf-8 -*-
from openprocurement.tender.belowthreshold.tests.base import test_organization

# TenderAwardResourceTest


def create_tender_award_invalid(self):
    self.app.authorization = ('Basic', ('token', ''))
    request_path = '/tenders/{}/awards'.format(self.tender_id)
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
        'data': {'suppliers': [{'identifier': 'invalid_value'}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'identifier': [
            u'Please use a mapping for this field or Identifier instance instead of unicode.']}, u'location': u'body',
            u'name': u'suppliers'}
    ])

    response = self.app.post_json(request_path, {
        'data': {'suppliers': [{'identifier': {'id': 0}}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [
            {u'contactPoint': [u'This field is required.'], u'identifier': {u'scheme': [u'This field is required.']},
             u'name': [u'This field is required.'], u'address': [u'This field is required.']}], u'location': u'body',
         u'name': u'suppliers'},
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'bid_id'}
    ])

    response = self.app.post_json(request_path, {'data': {'suppliers': [
        {'name': 'name', 'identifier': {'uri': 'invalid_value'}}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [{u'contactPoint': [u'This field is required.'],
                           u'identifier': {u'scheme': [u'This field is required.'], u'id': [u'This field is required.'],
                                           u'uri': [u'Not a well formed URL.']},
                           u'address': [u'This field is required.']}], u'location': u'body', u'name': u'suppliers'},
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'bid_id'}
    ])

    response = self.app.post_json(request_path, {'data': {
        'suppliers': [test_organization],
        'status': 'pending',
        'bid_id': self.initial_bids[0]['id'],
        'lotID': '0' * 32
    }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'lotID should be one of lots'], u'location': u'body', u'name': u'lotID'}
    ])

    response = self.app.post_json('/tenders/some_id/awards', {'data': {
        'suppliers': [test_organization], 'bid_id': self.initial_bids[0]['id']}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'tender_id'}
    ])

    response = self.app.get('/tenders/some_id/awards', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'tender_id'}
    ])

    self.set_status('complete')

    bid = self.initial_bids[0]
    response = self.app.post_json('/tenders/{}/awards'.format(
        self.tender_id), {
        'data': {'suppliers': [test_organization], 'status': 'pending', 'bid_id': self.initial_bids[0]['id'],
                 'lotID': bid['lotValues'][0]['relatedLot']}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't create award in current (complete) tender status")


def create_tender_award(self):
    response = self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], u'active')

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], u'active.awarded')

    response = self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "cancelled"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], u'cancelled')
    self.assertIn('Location', response.headers)


def patch_tender_award(self):
    response = self.app.patch_json('/tenders/{}/awards/some_id'.format(self.tender_id),
                                   {"data": {"status": "unsuccessful"}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'award_id'}
    ])

    response = self.app.patch_json('/tenders/some_id/awards/some_id', {"data": {"status": "unsuccessful"}}, status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'tender_id'}
    ])

    response = self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"awardStatus": "unsuccessful"}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {"location": "body", "name": "awardStatus", "description": "Rogue field"}
    ])

    response = self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('Location', response.headers)
    new_award_location = response.headers['Location']

    response = self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "pending"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update award in current (unsuccessful) status")

    response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 2)
    self.assertIn(response.json['data'][1]['id'], new_award_location)
    new_award = response.json['data'][-1]

    response = self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, new_award['id'], self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 2)

    response = self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, new_award['id'], self.tender_token),
        {"data": {"status": "cancelled"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('Location', response.headers)

    response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 3)

    self.set_status('complete')

    response = self.app.get('/tenders/{}/awards/{}'.format(self.tender_id, self.award_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["value"]["amount"], 469.0)

    response = self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "unsuccessful"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't update award in current (complete) tender status")


def patch_tender_award_active(self):
    request_path = '/tenders/{}/awards'.format(self.tender_id)
    response = self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('Location', response.headers)
    new_award_location = response.headers['Location']

    response = self.app.patch_json(new_award_location[-81:] + '?acc_token={}'.format(self.tender_token),
                                   {"data": {"status": "active", "qualified": True, "eligible": True}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotIn('Location', response.headers)

    response = self.app.get(request_path)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 2)

    response = self.app.post_json(new_award_location[-81:] + '/complaints?acc_token={}'.format(self.bid_token),
                                  {'data': {
                                      'title': 'complaint title',
                                      'description': 'complaint description',
                                      'author': test_organization,
                                      'status': 'pending'
                                  }})
    self.assertEqual(response.status, '201 Created')

    self.app.authorization = ('Basic', ('reviewer', ''))
    response = self.app.patch_json(new_award_location[-81:] + '/complaints/{}'.format(response.json['data']['id']),
                                   {'data': {
                                       'status': 'accepted'
                                   }})
    self.assertEqual(response.status, '200 OK')

    response = self.app.patch_json(new_award_location[-81:] + '/complaints/{}'.format(response.json['data']['id']),
                                   {'data': {
                                       'status': 'satisfied'
                                   }})
    self.assertEqual(response.status, '200 OK')

    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json('{}/complaints?acc_token={}'.format(new_award_location[-81:], self.bid_token),
                                  {'data': {
                                      'title': 'complaint title',
                                      'description': 'complaint description',
                                      'author': test_organization
                                  }})
    self.assertEqual(response.status, '201 Created')

    response = self.app.patch_json(new_award_location[-81:] + '?acc_token={}'.format(self.tender_token),
                                   {"data": {"status": "cancelled"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('Location', response.headers)
    new_award_location = response.headers['Location']

    response = self.app.patch_json(new_award_location[-81:] + '?acc_token={}'.format(self.tender_token),
                                   {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('Location', response.headers)
    new_award_location = response.headers['Location']

    response = self.app.patch_json(new_award_location[-81:] + '?acc_token={}'.format(self.tender_token),
                                   {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotIn('Location', response.headers)

    response = self.app.get(request_path)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 4)


def patch_tender_award_unsuccessful(self):
    request_path = '/tenders/{}/awards'.format(self.tender_id)
    response = self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('Location', response.headers)
    new_award_location = response.headers['Location']

    response = self.app.patch_json(new_award_location[-81:] + '?acc_token={}'.format(self.tender_token),
                                   {"data": {"status": "active", "qualified": True, "eligible": True}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotIn('Location', response.headers)

    response = self.app.get(request_path)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 2)

    response = self.app.post_json(
        '/tenders/{}/awards/{}/complaints?acc_token={}'.format(self.tender_id, self.award_id, self.bid_token),
        {'data': {
            'title': 'complaint title',
            'description': 'complaint description',
            'author': test_organization,
            'status': 'pending'
        }})
    self.assertEqual(response.status, '201 Created')

    self.app.authorization = ('Basic', ('reviewer', ''))
    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, self.award_id, response.json['data']['id']),
        {'data': {
            'status': 'accepted'
        }})
    self.assertEqual(response.status, '200 OK')

    response = self.app.patch_json(
        '/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, self.award_id, response.json['data']['id']),
        {'data': {
            'status': 'satisfied'
        }})
    self.assertEqual(response.status, '200 OK')

    self.app.authorization = ('Basic', ('broker', ''))
    response = self.app.post_json('{}/complaints?acc_token={}'.format(new_award_location[-81:], self.bid_token),
                                  {'data': {
                                      'title': 'complaint title',
                                      'description': 'complaint description',
                                      'author': test_organization
                                  }})
    self.assertEqual(response.status, '201 Created')

    response = self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "cancelled"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('Location', response.headers)
    new_award_location = response.headers['Location']

    response = self.app.patch_json(new_award_location[-81:] + '?acc_token={}'.format(self.tender_token),
                                   {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('Location', response.headers)
    new_award_location = response.headers['Location']

    response = self.app.patch_json(new_award_location[-81:] + '?acc_token={}'.format(self.tender_token),
                                   {"data": {"status": "unsuccessful"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertNotIn('Location', response.headers)

    response = self.app.get(request_path)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 4)


def get_tender_award(self):
    response = self.app.get('/tenders/{}/awards/{}'.format(self.tender_id, self.award_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    award_data = response.json['data']

    response = self.app.get('/tenders/{}/awards/some_id'.format(self.tender_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'award_id'}
    ])

    response = self.app.get('/tenders/some_id/awards/some_id', status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'url', u'name': u'tender_id'}
    ])


def patch_tender_award_Administrator_change(self):
    self.app.authorization = ('Basic', ('token', ''))
    response = self.app.post_json('/tenders/{}/awards'.format(
        self.tender_id), {
        'data': {'suppliers': [test_organization], 'status': 'pending', 'bid_id': self.initial_bids[0]['id'],
                 'lotID': self.initial_lots[0]['id']}})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    award = response.json['data']
    complaintPeriod = award['complaintPeriod'][u'startDate']

    self.app.authorization = ('Basic', ('administrator', ''))
    response = self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, award['id']),
                                   {"data": {"complaintPeriod": {"endDate": award['complaintPeriod'][u'startDate']}}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn("endDate", response.json['data']['complaintPeriod'])
    self.assertEqual(response.json['data']['complaintPeriod']["endDate"], complaintPeriod)

# TenderLotAwardResourceTest


def create_tender_lot_award(self):
        self.app.authorization = ('Basic', ('token', ''))
        request_path = '/tenders/{}/awards'.format(self.tender_id)
        response = self.app.post_json(request_path, {'data': {'suppliers': [test_organization], 'status': 'pending', 'bid_id': self.initial_bids[0]['id']}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'], [
            {"location": "body", "name": "lotID", "description": ["This field is required."]}
        ])

        response = self.app.post_json(request_path, {'data': {'suppliers': [test_organization], 'status': 'pending', 'bid_id': self.initial_bids[0]['id'], 'lotID': self.initial_lots[0]['id']}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        award = response.json['data']
        self.assertEqual(award['suppliers'][0]['name'], test_organization['name'])
        self.assertEqual(award['lotID'], self.initial_lots[0]['id'])
        self.assertIn('id', award)
        self.assertIn(award['id'], response.headers['Location'])

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get(request_path)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'][-1], award)

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award['id'], self.tender_token), {"data": {"status": "active", "qualified": True, "eligible": True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'active')

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'active.awarded')

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award['id'], self.tender_token), {"data": {"status": "cancelled"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'cancelled')
        self.assertIn('Location', response.headers)


def patch_tender_lot_award(self):
        response = self.app.patch_json('/tenders/{}/awards/some_id'.format(self.tender_id), {"data": {"status": "unsuccessful"}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        response = self.app.patch_json('/tenders/some_id/awards/some_id', {"data": {"status": "unsuccessful"}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token), {"data": {"awardStatus": "unsuccessful"}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'], [
            {"location": "body", "name": "awardStatus", "description": "Rogue field"}
        ])

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token), {"data": {"status": "unsuccessful"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)
        new_award_location = response.headers['Location']

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token), {"data": {"status": "pending"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update award in current (unsuccessful) status")

        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 2)
        self.assertIn(response.json['data'][-1]['id'], new_award_location)
        new_award = response.json['data'][-1]

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, new_award['id'], self.tender_token), {"data": {"status": "active", "eligible": True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 2)

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, new_award['id'], self.tender_token), {"data": {"status": "cancelled"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)

        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 3)

        self.set_status('complete')

        response = self.app.get('/tenders/{}/awards/{}'.format(self.tender_id, self.award_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["value"]["amount"], 469.0)

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token), {"data": {"status": "unsuccessful"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update award in current (complete) tender status")


def patch_tender_lot_award_unsuccessful(self):
        request_path = '/tenders/{}/awards'.format(self.tender_id)
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token), {"data": {"status": "unsuccessful"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)
        new_award_location = response.headers['Location']

        response = self.app.patch_json(new_award_location[-81:]+'?acc_token={}'.format(self.tender_token), {"data": {"status": "active", "qualified": True, "eligible": True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertNotIn('Location', response.headers)

        response = self.app.get(request_path)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 2)

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(self.tender_id, self.award_id, self.bid_token), {'data': {
            'title': 'complaint title',
            'description': 'complaint description',
            'author': test_organization,
            'status': 'pending'
        }})
        self.assertEqual(response.status, '201 Created')

        self.app.authorization = ('Basic', ('reviewer', ''))
        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(self.tender_id, self.award_id, response.json['data']['id'], self.bid_token), {'data': {
            'status': 'accepted'
        }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(self.tender_id, self.award_id, response.json['data']['id'], self.bid_token), {'data': {
            'status': 'satisfied'
        }})
        self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('{}/complaints?acc_token={}'.format(new_award_location[-81:], self.bid_token), {'data': {
            'title': 'complaint title',
            'description': 'complaint description',
            'author': test_organization
        }})
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token), {"data": {"status": "cancelled"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)
        new_award_location = response.headers['Location']

        response = self.app.patch_json(new_award_location[-81:]+'?acc_token={}'.format(self.tender_token), {"data": {"status": "unsuccessful"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)
        new_award_location = response.headers['Location']

        response = self.app.patch_json(new_award_location[-81:]+'?acc_token={}'.format(self.tender_token), {"data": {"status": "unsuccessful"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertNotIn('Location', response.headers)

        response = self.app.get(request_path)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 4)

# Tender2LotAwardResourceTest


def create_tender_2lot_award(self):
    request_path = '/tenders/{}/awards'.format(self.tender_id)
    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]['id']
    }})
    self.assertEqual(response.status, '201 Created')

    self.app.authorization = ('Basic', ('token', ''))
    response = self.app.post_json(request_path, {'data': {
        'suppliers': [test_organization],
        'status': 'pending',
        'bid_id': self.initial_bids[0]['id'],
        'lotID': self.initial_lots[0]['id']
    }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can create award only in active lot status")

    response = self.app.post_json(request_path, {'data': {
        'suppliers': [test_organization],
        'status': 'pending',
        'bid_id': self.initial_bids[0]['id'],
        'lotID': self.initial_lots[1]['id']
    }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    award = response.json['data']
    self.assertEqual(award['suppliers'][0]['name'], test_organization['name'])
    self.assertEqual(award['lotID'], self.initial_lots[1]['id'])
    self.assertIn('id', award)
    self.assertIn(award['id'], response.headers['Location'])

    response = self.app.get(request_path)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'][-1], award)

    response = self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, award['id']), {"data": {"status": "active", "qualified": True, "eligible": True}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], u'active')

    response = self.app.get('/tenders/{}'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], u'active.awarded')

    response = self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, award['id']), {"data": {"status": "cancelled"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], u'cancelled')
    self.assertIn('Location', response.headers)


def patch_tender_2lot_award(self):
    request_path = '/tenders/{}/awards'.format(self.tender_id)
    response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token), {"data": {"status": "active", "qualified": True, "eligible": True}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    response = self.app.get(request_path)
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(len(response.json['data']), 2)
    new_award = response.json['data'][-1]

    response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[1]['id']
    }})
    self.assertEqual(response.status, '201 Created')

    response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, new_award['id'], self.tender_token), {"data": {"status": "unsuccessful"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can update award only in active lot status")


# TenderAwardComplaintDocumentResourceTest


def patch_tender_award_complaint_document(self):
    response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
        self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}/documents/{}'.format(self.tender_id, self.award_id, self.complaint_id, doc_id), {"data": {"description": "document description"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can update document only author")

    response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token), {"data": {"description": "document description"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents/{}'.format(
        self.tender_id, self.award_id, self.complaint_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('document description', response.json["data"]["description"])

    response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token), {"data": {
        "status": "pending",
    }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']["status"], "pending")

    response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token), 'content2', content_type='application/msword')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents/{}?{}'.format(
        self.tender_id, self.award_id, self.complaint_id, doc_id, key))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, 'content2')

    self.set_status('complete')

    response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token), {"data": {"description": "document description"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (complete) tender status")


# Tender2LotAwardComplaintDocumentResourceTest


def create_tender_2lot_award_complaint_document(self):
    response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents'.format(
        self.tender_id, self.award_id, self.complaint_id), upload_files=[('file', 'name.doc', 'content')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (draft) complaint status")

    response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
        self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual('name.doc', response.json["data"]["title"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents'.format(self.tender_id, self.award_id, self.complaint_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual('name.doc', response.json["data"][0]["title"])

    response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents?all=true'.format(self.tender_id, self.award_id, self.complaint_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual('name.doc', response.json["data"][0]["title"])

    response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents/{}?download=some_id'.format(
        self.tender_id, self.award_id, self.complaint_id, doc_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
    ])

    response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents/{}?{}'.format(
        self.tender_id, self.award_id, self.complaint_id, doc_id, key))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 7)
    self.assertEqual(response.body, 'content')

    response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents/{}'.format(
        self.tender_id, self.award_id, self.complaint_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('name.doc', response.json["data"]["title"])

    response = self.app.post_json('/tenders/{}/cancellations'.format(self.tender_id), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]['id']
    }})
    self.assertEqual(response.status, '201 Created')

    response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents'.format(
        self.tender_id, self.award_id, self.complaint_id), upload_files=[('file', 'name.doc', 'content')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (unsuccessful) tender status")


def put_tender_2lot_award_complaint_document(self):
    response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
        self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}'.format(self.tender_id, self.award_id, self.complaint_id, doc_id),
                            status=404,
                            upload_files=[('invalid_name', 'name.doc', 'content')])
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location':
            u'body', u'name': u'file'}
    ])

    response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}'.format(
        self.tender_id, self.award_id, self.complaint_id, doc_id), upload_files=[('file', 'name.doc', 'content2')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can update document only author")

    response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
        self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token), upload_files=[('file', 'name.doc', 'content2')])
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents/{}?{}'.format(
        self.tender_id, self.award_id, self.complaint_id, doc_id, key))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, 'content2')

    response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents/{}'.format(
        self.tender_id, self.award_id, self.complaint_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('name.doc', response.json["data"]["title"])

    response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
        self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token), 'content3', content_type='application/msword')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents/{}?{}'.format(
        self.tender_id, self.award_id, self.complaint_id, doc_id, key))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, 'content3')

    response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token), {"data": {
        "status": "pending",
    }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']["status"], "pending")

    response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token), 'content4', content_type='application/msword')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    key = response.json["data"]["url"].split('?')[-1]

    response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents/{}?{}'.format(
        self.tender_id, self.award_id, self.complaint_id, doc_id, key))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/msword')
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, 'content4')

    response = self.app.post_json('/tenders/{}/cancellations'.format(self.tender_id), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]['id']
    }})
    self.assertEqual(response.status, '201 Created')

    response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
        self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token), upload_files=[('file', 'name.doc', 'content3')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (unsuccessful) tender status")


def patch_tender_2lot_award_complaint_document(self):
    response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
        self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}/documents/{}'.format(self.tender_id, self.award_id, self.complaint_id, doc_id), {"data": {"description": "document description"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can update document only author")

    response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token), {"data": {"description": "document description"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents/{}'.format(
        self.tender_id, self.award_id, self.complaint_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual('document description', response.json["data"]["description"])

    response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token), {"data": {
        "status": "pending",
    }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.json['data']["status"], "pending")

    response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token), {"data": {"description": "document description2"}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']["description"], "document description2")

    response = self.app.post_json('/tenders/{}/cancellations'.format(self.tender_id), {'data': {
        'reason': 'cancellation reason',
        'status': 'active',
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]['id']
    }})
    self.assertEqual(response.status, '201 Created')

    response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token), {"data": {"description": "document description"}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (unsuccessful) tender status")
