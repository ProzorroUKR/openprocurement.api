# -*- coding: utf-8 -*-
import unittest

from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUContentWebTest,
    test_tender_data_eu,
    test_features_tender_eu_data,
    test_bids_eu as test_bids
)
from openprocurement.tender.openeu.tests.base import (
    test_tender_data,
    test_features_tender_data as test_features_tender_eu_data
)

test_bids.append(test_bids[0].copy())  # Minimal number of bits is 3


class CompetitiveDialogEUBidResourceTest(BaseCompetitiveDialogEUContentWebTest):

    initial_status = 'active.tendering'
    initial_auth = ('Basic', ('broker', ''))

    def test_create_tender_bidder_invalid(self):
        """
          Test create dialog bidder invalid
        """
        # Try create bid by bad tender id
        response = self.app.post_json('/tenders/some_id/bids',
                                      {'data': {'tenderers': test_bids[0]['tenderers'],
                                                'value': {'amount': 500}}},
                                      status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        request_path = '/tenders/{}/bids'.format(self.tender_id)
        # Try create bid without content type
        response = self.app.post(request_path, 'data', status=415)
        self.assertEqual(response.status, '415 Unsupported Media Type')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description':
                u"Content-Type header should be one of ['application/json']", u'location': u'header', u'name': u'Content-Type'}
        ])

        # Try create bid with bad json
        response = self.app.post(request_path, 'data', content_type='application/json', status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'No JSON object could be decoded',
                u'location': u'body', u'name': u'data'}
        ])

        # Try create bid with invalid data
        response = self.app.post_json(request_path, 'data', status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Data not available',
                u'location': u'body', u'name': u'data'}
        ])

        # Try create bid with bad data
        response = self.app.post_json(request_path, {'not_data': {}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Data not available',
                u'location': u'body', u'name': u'data'}
        ])

        # Try create bid with invalid fields
        response = self.app.post_json(request_path, {'data': {'invalid_field': 'invalid_value'}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Rogue field', u'location':
                u'body', u'name': u'invalid_field'}
        ])

        # Try create bid with invalid identifier
        response = self.app.post_json(request_path, {'data': {'tenderers': [{'identifier': 'invalid'}]}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': {u'identifier': [
                u'Please use a mapping for this field or Identifier instance instead of unicode.']}, u'location': u'body', u'name': u'tenderers'}
        ])

        # Try create bid without required fields
        response = self.app.post_json(request_path, {'data': {'tenderers': [{'identifier': {}}]}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'selfEligible'},
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'selfQualified'},
            {u'description': [
                {u'contactPoint': [u'This field is required.'], u'identifier': {u'scheme': [u'This field is required.'], u'id': [u'This field is required.']},
                 u'name': [u'This field is required.'],
                 u'address': [u'This field is required.']}
            ], u'location': u'body', u'name': u'tenderers'}
        ])

        # Try create bid with invalid identifier.uri
        response = self.app.post_json(request_path, {'data': {'selfEligible': False,
                                                              'tenderers': [{'name': 'name',
                                                                             'identifier': {'uri': 'invalid_value'}}]}
                                                     },
                                      status=422)
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

        # Try create bid without description
        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers']}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'value'}
        ])

        # Try create bid with bad valueAddedTaxIncluded
        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers'],
                                                              'value': {'amount': 500, 'valueAddedTaxIncluded': False}}
                                                     },
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of tender'], u'location': u'body', u'name': u'value'}
        ])

        # Try create bid bad currency
        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers'],
                                                              "value": {"amount": 500, 'currency': "USD"}}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')

        self.assertEqual(response.json['errors'], [
            {u'description': [u'currency of bid should be identical to currency of value of tender'], u'location': u'body', u'name': u'value'},
        ])

    def test_create_tender_bidder(self):
        """ Test create dialog bdder """
        # Create bid,
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                       'tenderers': test_bids[0]['tenderers'], "value": {"amount": 500}}
                                       })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bid = response.json['data']
        self.assertEqual(bid['tenderers'][0]['name'], test_bids[0]['tenderers'][0]['name'])
        self.assertIn('id', bid)
        self.assertIn(bid['id'], response.headers['Location'])

        # Create bids in all possible statues
        for status in ('active', 'unsuccessful', 'deleted', 'invalid'):
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                          {'data': {'selfEligible': True, 'selfQualified': True,
                                                    'tenderers': test_bids[0]['tenderers'],
                                                    'value': {"amount": 500},
                                                    'status': status}})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.json['data']['status'], status)

        self.set_status('complete')  # set tender status to complete

        # Try create bid when tender status is complete
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                       'tenderers': test_bids[0]['tenderers'], "value": {"amount": 500}}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add bid in current (complete) tender status")

    def test_patch_tender_bidder(self):
        """
          Test path dialog bidder
        """
        # Create test bidder
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                       'tenderers': test_bids[0]['tenderers'], "value": {"amount": 500}}
                                       })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bid = response.json['data']
        bid_token = response.json['access']['token']

        # Try set bidder amount bigger then tender
        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token),
                                       {'data': {'value': {'amount': 600}}},
                                       status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'value of bid should be less than value of tender'], u'location': u'body', u'name': u'value'}
        ])

        # Update tenders[0].name, and check response fields
        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token),
                                       {"data": {'tenderers': [{"name": u"Державне управління управлінням справами"}]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['date'], bid['date'])
        self.assertNotEqual(response.json['data']['tenderers'][0]['name'], bid['tenderers'][0]['name'])

        # Update bidder amount and tender
        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token),
                                       {"data": {"value": {"amount": 500}, 'tenderers': test_bids[0]['tenderers']}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['date'], bid['date'])
        self.assertEqual(response.json['data']['tenderers'][0]['name'], bid['tenderers'][0]['name'])

        # Update bidder amount
        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token),
                                       {"data": {"value": {"amount": 400}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["value"]["amount"], 400)
        self.assertNotEqual(response.json['data']['date'], bid['date'])

        # Try update bidder amount by bad bidder id
        response = self.app.patch_json('/tenders/{}/bids/some_id?acc_token={}'.format(self.tender_id, bid_token),
                                       {"data": {"value": {"amount": 400}}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'bid_id'}
        ])

        # Try update bidder amount by bad dialog id
        response = self.app.patch_json('/tenders/some_id/bids/some_id', {"data": {"value": {"amount": 40}}},status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        # Try update bidder status
        for status in ('invalid', 'active', 'unsuccessful', 'deleted'):
            response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token),
                                        {'data': {'status': status}}, status=403)
            self.assertEqual(response.status, '403 Forbidden')
            self.assertEqual(response.json['errors'][0]["description"], "Can't update bid to ({}) status".format(status))

        self.set_status('complete')  # Set dialog to status complete

        # Get bidder by id
        response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, bid['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["value"]["amount"], 400)

        # Try update bidder when dialog status is complete
        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token),
                                       {"data": {"value": {"amount": 400}}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update bid in current (complete) tender status")

    def test_get_tender_bidder(self):
        """
          Try get bidder on different tender status
        """
        # Create bidder, and save
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                       'tenderers': test_bids[0]['tenderers'], "value": {"amount": 500}}
                                       })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bid = response.json['data']
        bid_token = response.json['access']['token']

        # Create another bidder
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                                'tenderers': test_bids[0]['tenderers'], "value": {"amount": 499}}})

        # Create another 2 bidder
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                       'tenderers': test_bids[0]['tenderers'], "value": {"amount": 499}}})

        # Try get bidder when dialog status active.tendering
        response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, bid['id']), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't view bid in current (active.tendering) tender status")

        # Get bidder by owner token
        response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], bid)

        # switch to active.pre-qualification, and check chronograph work
        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        # Get bidders when dialog status is pre-qualification
        self.app.authorization = ('Basic', ('anon', ''))
        response = self.app.get('/tenders/{}/bids'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 3)
        for b in response.json['data']:
            self.assertEqual(set(b.keys()), set(['id', 'status', 'tenderers']))

        # Get bidder
        response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, bid['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(set(response.json['data'].keys()), set(['id', 'status', 'tenderers']))

        # qualify bids
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.app.authorization = ('Basic', ('token', ''))
        for qualification in response.json['data']:  # TODO: must fail, because qualification.py not found
            response = self.app.patch_json('/tenders/{}/qualifications/{}'.format(self.tender_id, qualification['id']),
                                           {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, "200 OK")

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"status": 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        # Get bids by anon user
        self.app.authorization = ('Basic', ('anon', ''))
        response = self.app.get('/tenders/{}/bids'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 3)
        for b in response.json['data']:
            self.assertEqual(set(b.keys()), set(['id', 'status', 'tenderers']))

        # Get bidder by anon user
        response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, bid['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(set(response.json['data'].keys()), set(['id', 'status', 'tenderers']))

        # try switch to active.stage2.pending
        self.set_status('active.stage2.pending', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id),
                                       {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], "active.stage2.pending")

        # switch to qualification
        self.app.authorization = ('Basic', ('auction', ''))
        self.app.get('/tenders/{}/auction'.format(self.tender_id), status=404)  # Try get action
        self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': {'bids': {}}}, status=404)  # Try update auction

        response = self.app.get('/tenders/{}'.format(self.tender_id))  # Get dialog and check status
        self.assertEqual(response.json['data']['status'], "active.stage2.pending")

    def test_deleted_bid_is_not_restorable(self):
        """
          Restore bid after delete
        """
        response = self.app.post_json('/tenders/{}/bids'.format(
            self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                       'tenderers': test_bids[0]['tenderers'], "value": {"amount": 500}}})
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
                                       {"data": {'status': 'pending'}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertNotEqual(response.json['data']['status'], 'deleted')
        self.assertEqual(response.json['data']['status'], 'pending')

    def test_deleted_bid_do_not_locks_tender_in_state(self):
        bids = []
        bids_tokens = []
        for bid_amount in (400, 405):  # Create two bids
            response = self.app.post_json('/tenders/{}/bids'.format(
                self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                           'tenderers': test_bids[0]['tenderers'], "value": {"amount": bid_amount}}})
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

        # Create new bid
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                       'tenderers': test_bids[1]['tenderers'], "value": {"amount": 101}}})
        # Create new bid
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                                'tenderers': test_bids[1]['tenderers'], "value": {"amount": 101}}})

        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        # Update tender status
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        # qualify bids
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.app.authorization = ('Basic', ('token', ''))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}'.format(self.tender_id, qualification['id']),
                                           {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, "200 OK")

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id),
                                       {"data": {"status": 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        # switch to active.stage2.pending
        self.set_status('active.stage2.pending', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], "active.stage2.pending")

        # switch to qualification
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id), status=404)

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertNotEqual(response.json['data']['status'], "active.qualification")
        self.assertEqual(response.json['data']['status'], 'active.stage2.pending')

        # check bids
        self.app.authorization = ('Basic', ('anon', ''))
        response = self.app.get('/tenders/{}/bids'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        for b in response.json['data']:
            if b['status'] in [u'invalid', u'deleted']:
                self.assertEqual(set(b.keys()), set(['id', 'status']))
            else:
                self.assertEqual(set(b.keys()), set(['id', 'status', 'tenderers']))

    def test_get_tender_tenderers(self):
        # Create bid
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                       'tenderers': test_bids[0]['tenderers'], "value": {"amount": 500}}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bid = response.json['data']  # Save bid

        # Try get bid when dialog status is active.tendering by owner
        response = self.app.get('/tenders/{}/bids'.format(self.tender_id), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't view bids in current (active.tendering) tender status")

        # Create bid
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                       'tenderers': test_bids[1]['tenderers'], "value": {"amount": 101}}})
        # Create another bid
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                                'tenderers': test_bids[2]['tenderers'], "value": {"amount": 111}}})

        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        # qualify bids
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.app.authorization = ('Basic', ('token', ''))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}'.format(self.tender_id, qualification['id']),
                                           {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, "200 OK")

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id),
                                       {"data": {"status": 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        # switch to active.stage2.pending
        self.set_status('active.stage2.pending', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], "active.stage2.pending")

        response = self.app.get('/tenders/some_id/bids', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

    def test_bids_invalidation_on_tender_change(self):
        """
          Test bids status when tender is changing
        """
        bids_access = {}

        # submit bids
        for data in test_bids:
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': data})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            bids_access[response.json['data']['id']] = response.json['access']['token']

        # check initial status
        for bid_id, token in bids_access.items():
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid_id, token))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'pending')

        # update tender. we can set value that is less than a value in bids as
        # they will be invalidated by this request
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"value": {"amount": 300.0}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']["value"]["amount"], 300)

        # check bids status
        for bid_id, token in bids_access.items():
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid_id, token))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'invalid')
        # try to add documents to bid
        doc_resource = 'documents'
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, bid_id,
                                                                              doc_resource, token),
                                 upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')],
                                 status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add document to 'invalid' bid")

        # we don't support another type of documents
        for doc_resource in ['qualification_documents', 'eligibility_documents', 'financial_documents']:
            response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, bid_id,
                                                                                  doc_resource, token),
                                     upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')],
                                     status=404)

        # check that tender status change does not invalidate bids
        # submit one more bid. check for invalid value first
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': test_bids[0]}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'value of bid should be less than value of tender'], u'location': u'body',
             u'name': u'value'}
        ])
        # and submit valid bid
        data = test_bids[0]
        data['value']['amount'] = 299
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': data})
        self.assertEqual(response.status, '201 Created')
        valid_bid_id = response.json['data']['id']

        self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                           {'data': {'selfEligible': True, 'selfQualified': True,
                            'tenderers': test_bids[1]['tenderers'], "value": {"amount": 101}}})

        self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                           {'data': {'selfEligible': True, 'selfQualified': True,
                            'tenderers': test_bids[2]['tenderers'], "value": {"amount": 101}}})

        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id),
                                       {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        # qualify bids
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.app.authorization = ('Basic', ('token', ''))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}'.format(self.tender_id, qualification['id']),
                                           {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, "200 OK")

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id),
                                       {"data": {"status": 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        # switch to active.stage2.pending
        self.set_status('active.stage2.pending', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], "active.stage2.pending")

        # Try switch to qualification
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id), status=404)
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertNotEqual(response.json['data']['status'], "active.auction")
        self.assertEqual(response.json['data']['status'], "active.stage2.pending")

        # tender should display all bids
        self.app.authorization = ('Basic', ('anon', ''))
        response = self.app.get('/tenders/{}/bids'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 7)
        for b in response.json['data']:
            if b['status'] == u'invalid':
                self.assertEqual(set(b.keys()), set(['id', 'status']))
            else:
                self.assertEqual(set(b.keys()), set(['id', 'status', 'tenderers']))

        # invalidated bids stay invalidated
        for bid_id, token in bids_access.items():
            response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, bid_id))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'invalid')
            # invalidated bids displays only 'id' and 'status' fields
            self.assertFalse('value' in response.json['data'])
            self.assertFalse('tenderers' in response.json['data'])
            self.assertFalse('date' in response.json['data'])

        # check bids availability on finished tender
        self.set_status('complete')
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']['bids']), 7)
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

    def test_bids_activation_on_tender_documents(self):
        """
          test bids activation on tender documents
        """
        bids_access = {}

        # submit bids
        for data in test_bids:
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': data})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            bids_access[response.json['data']['id']] = response.json['access']['token']

        # check initial status
        for bid_id, token in bids_access.items():
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid_id, token))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'pending')

        response = self.app.post('/tenders/{}/documents?acc_token={}'.format(self.tender_id, self.tender_token),
                                 upload_files=[('file', u'укр.doc', 'content')])
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


class CompetitiveDialogEUBidFeaturesResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_data = test_features_tender_eu_data
    initial_status = 'active.tendering'
    initial_auth = ('Basic', ('broker', ''))

    def test_features_bidder(self):
        test_features_bids = [
            {
                # "status": "pending",
                "parameters": [
                    {
                        "code": i["code"],
                        "value": 0.1,
                    }
                    for i in self.initial_data['features']
                ],
                "tenderers": test_bids[0]["tenderers"],
                "value": {
                    "amount": 469,
                    "currency": "UAH",
                    "valueAddedTaxIncluded": True
                },
                'selfQualified': True,
                'selfEligible': True
            },
            {
                "status": "pending",
                "parameters": [
                    {
                        "code": i["code"],
                        "value": 0.15,
                    }
                    for i in self.initial_data['features']
                ],
                "tenderers": test_bids[1]["tenderers"],
                "value": {
                    "amount": 479,
                    "currency": "UAH",
                    "valueAddedTaxIncluded": True
                },
                'selfQualified': True,
                'selfEligible': True
            },
        ]
        for i in test_features_bids:
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': i})
            i['status'] = "pending"
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            bid = response.json['data']
            bid.pop(u'date')
            bid.pop(u'id')
            self.assertEqual(bid, i)

    def test_features_bidder_invalid(self):
        data = {
            "tenderers": test_bids[0]["tenderers"],
            "value": {
                "amount": 469,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            },
            'selfQualified': True,
            'selfEligible': True
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


class CompetitiveDialogEUBidDocumentResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_auth = ('Basic', ('broker', ''))
    initial_status = 'active.tendering'

    def setUp(self):
        super(CompetitiveDialogEUBidDocumentResourceTest, self).setUp()
        # Create bid
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': test_bids[0]})
        bid = response.json['data']
        self.bid_id = bid['id']
        self.bid_token = response.json['access']['token']
        # create second bid
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': test_bids[1]})
        bid2 = response.json['data']
        self.bid2_id = bid2['id']
        self.bid2_token = response.json['access']['token']

        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': test_bids[1]})
        bid3 = response.json['data']
        self.bid3_id = bid3['id']
        self.bid3_token = response.json['access']['token']

    def test_get_tender_bidder_document(self):

        doc_id_by_type = {}
        # self.app.authorization = ('Basic', ('anon', ''))

        def document_is_unaccessible_for_others(resource):
            orig_auth = self.app.authorization
            self.app.authorization = ('Basic', ('broker05', ''))
            response = self.app.get('/tenders/{}/bids/{}/{}'.format(self.tender_id, self.bid_id, resource), status=403)
            self.assertEqual(response.status, '403 Forbidden')
            doc_id = doc_id_by_type[resource]['id']
            response = self.app.get('/tenders/{}/bids/{}/{}/{}'.format(self.tender_id, self.bid_id, resource, doc_id),
                                    status=403)
            self.assertEqual(response.status, '403 Forbidden')
            self.app.authorization = orig_auth

        def document_is_unaccessible_for_tender_owner(resource):
            orig_auth = self.app.authorization
            self.app.authorization = ('Basic', ('broker', ''))
            response = self.app.get('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                 resource, self.tender_token),
                                    status=403)
            self.assertEqual(response.status, '403 Forbidden')
            doc_id = doc_id_by_type[resource]['id']
            response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                    resource, doc_id, self.tender_token),
                                    status=403)
            self.assertEqual(response.status, '403 Forbidden')
            self.app.authorization = orig_auth

        def all_documents_are_accessible_for_bid_owner(resource):
            """
              Test that bid owner can get document by resource
            """
            orig_auth = self.app.authorization
            self.app.authorization = ('Basic', ('broker', ''))
            resource = 'documents'
            response = self.app.get('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                 resource, self.bid_token))
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
            response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                    resource, doc_id,
                                                                                    self.bid_token))
            self.assertEqual(response.status, '200 OK')
            self.assertIn('previousVersions', response.json['data'])
            doc = response.json['data']
            del doc['previousVersions']
            self.assertEqual(doc, doc1)
            doc_id = doc_id_by_type[resource+'private']['id']
            response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                    resource, doc_id,
                                                                                    self.bid_token))
            self.assertEqual(response.status, '200 OK')
            self.assertIn('previousVersions', response.json['data'])
            doc = response.json['data']
            del doc['previousVersions']
            self.assertEqual(doc, doc2)
            self.app.authorization = orig_auth

        def documents_are_accessible_for_t_and_b_owners(resource):
            """
              Tets that bid or tender owner can get documents
            """
            orig_auth = self.app.authorization
            self.app.authorization = ('Basic', ('broker', ''))
            for token in (self.bid_token, self.tender_token):
                response = self.app.get('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                     resource, token))
                self.assertEqual(response.status, '200 OK')
                self.assertEqual(len(response.json['data']), 2)
                doc_id = doc_id_by_type[resource]['id']
                response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                        resource, doc_id, token))
                self.assertEqual(response.status, '200 OK')
                doc_id = doc_id_by_type[resource+'private']['id']
                response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                        resource, doc_id, token))
                self.assertEqual(response.status, '200 OK')
            self.app.authorization = orig_auth

        def all_public_documents_are_accessible_for_others():
            """
              Test that documents are available for others user
            """
            orig_auth = self.app.authorization
            self.app.authorization = ('Basic', ('broker05', ''))
            doc_resource = 'documents'
            response = self.app.get('/tenders/{}/bids/{}/{}'.format(self.tender_id, self.bid_id, doc_resource))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(len(response.json['data']), 3)
            self.assertIn(doc_id_by_type[doc_resource]['key'], response.json['data'][0]['url'])
            self.assertNotIn('url', response.json['data'][1])
            response = self.app.get('/tenders/{}/bids/{}/{}/{}'.format(self.tender_id, self.bid_id, doc_resource,
                                                                       doc_id_by_type[doc_resource]['id']))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['title'], 'name_{}.doc'.format(doc_resource[:-1]))
            self.assertEqual(response.json['data']['confidentiality'], u'public')
            self.assertEqual(response.json['data']['format'], u'application/msword')
            self.assertEqual(response.json['data']['language'], 'uk')
            response = self.app.get('/tenders/{}/bids/{}/{}/{}'.format(self.tender_id, self.bid_id, doc_resource,
                                                                       doc_id_by_type[doc_resource+'private']['id']))
            self.assertEqual(response.status, '200 OK')
            self.assertNotIn('url', response.json['data'])
            self.app.authorization = orig_auth

        doc_resource = 'documents'
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                              doc_resource, self.bid_token),
                                 upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]
        doc_id_by_type[doc_resource] = {'id': doc_id, 'key': key}

        # upload private document
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                              doc_resource, self.bid_token),
                                 upload_files=[('file', 'name_{}_private.doc'.format(doc_resource[:-1]), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}_private.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]
        doc_id_by_type[doc_resource+'private'] = {'id': doc_id, 'key': key}
        response = self.app.patch_json(
            '/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, doc_resource,
                                                            doc_id, self.bid_token),
            {"data": {'confidentiality': 'buyerOnly',
                      'confidentialityRationale': 'Only our company sells badgers with pink hair.'}})
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
        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0].keys()), set(['id', 'status', 'documents', 'tenderers']))
        self.assertEqual(set(response.json['data'][1].keys()), set(['id', 'status', 'tenderers']))
        response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, self.bid_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(set(response.json['data'].keys()), set(['id', 'status', 'documents', 'tenderers']))
        response = self.app.get('/tenders/{}/bids/{}/documents'.format(self.tender_id, self.bid_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 2)
        self.assertIn(doc_id_by_type['documents']['key'], response.json['data'][0]['url'])
        doc_id = doc_id_by_type['documents']['id']
        response = self.app.get('/tenders/{}/bids/{}/documents/{}'.format(self.tender_id, self.bid_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['title'], u'name_document.doc')
        self.assertEqual(response.json['data']['confidentiality'], u'public')
        self.assertEqual(response.json['data']['format'], u'application/msword')
        self.assertEqual(response.json['data']['language'], 'uk')

        documents_are_accessible_for_t_and_b_owners("documents")

        # qualify bids
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.app.authorization = ('Basic', ('token', ''))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}'.format(self.tender_id,
                                                                                  qualification['id']),
                                           {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, "200 OK")

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id),
                                       {"data": {"status": 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        self.app.authorization = ('Basic', ('anon', ''))
        response = self.app.get('/tenders/{}/bids'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 3)
        self.assertEqual(set(response.json['data'][0].keys()), set(['id', 'status', 'documents', 'tenderers']))
        self.assertEqual(set(response.json['data'][1].keys()), set(['id', 'status', 'tenderers']))
        response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, self.bid_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(set(response.json['data'].keys()), set(['id', 'status', 'documents', 'tenderers']))
        response = self.app.get('/tenders/{}/bids/{}/documents'.format(self.tender_id, self.bid_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 2)
        self.assertIn(doc_id_by_type['documents']['key'], response.json['data'][0]['url'])
        doc_id = doc_id_by_type['documents']['id']
        response = self.app.get('/tenders/{}/bids/{}/documents/{}'.format(self.tender_id, self.bid_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['title'], u'name_document.doc')
        self.assertEqual(response.json['data']['confidentiality'], u'public')
        self.assertEqual(response.json['data']['format'], u'application/msword')
        documents_are_accessible_for_t_and_b_owners("documents")

    def test_create_tender_bidder_document(self):
        doc_id_by_type = {}

        # we don't support another type of documents
        for doc_resource in ['qualification_documents', 'eligibility_documents', 'financial_documents']:
            response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                  doc_resource, self.bid_token),
                                     upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')],
                                     status=404)

        # Create documents for bid
        doc_resource = 'documents'
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                              doc_resource, self.bid_token),
                                 upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']

        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]
        doc_id_by_type[doc_resource] = {'id': doc_id, 'key': key}

        doc_resource = 'documents'
        response = self.app.get('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                             doc_resource, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id_by_type[doc_resource]['id'], response.json["data"][0]["id"])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"][0]["title"])

        response = self.app.get('/tenders/{}/bids/{}/{}?all=true&acc_token={}'.format(self.tender_id,self.bid_id,
                                                                                      doc_resource, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id_by_type[doc_resource]['id'], response.json["data"][0]["id"])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"][0]["title"])

        doc_id = doc_id_by_type[doc_resource]['id']
        key = doc_id_by_type[doc_resource]['key']
        response = self.app.get('/tenders/{}/bids/{}/{}/{}?download=some_id&acc_token={}'.format(self.tender_id,
                                                                                                 self.bid_id,
                                                                                                 doc_resource,
                                                                                                 doc_id,
                                                                                                 self.bid_token),
                                status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
        ])

        response = self.app.get('/tenders/{}/bids/{}/{}/{}?{}'.format(self.tender_id, self.bid_id,
                                                                      doc_resource, doc_id, key),
                                status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) tender status")

        response = self.app.get('/tenders/{}/bids/{}/{}/{}?{}&acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                   doc_resource, doc_id, key,
                                                                                   self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 7)
        self.assertEqual(response.body, 'content')

        response = self.app.get('/tenders/{}/bids/{}/{}/{}'.format(self.tender_id, self.bid_id,
                                                                   doc_resource, doc_id),
                                status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) tender status")

        response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                doc_resource, doc_id,
                                                                                self.bid_token))
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

        doc_resource = 'documents'
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                              doc_resource, self.bid_token),
                                 upload_files=[('file', 'name.doc', 'content')],
                                 status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (active.pre-qualification) tender status")

        # list qualifications
        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, self.tender_token))
        self.assertEqual(response.status, "200 OK")
        # qualify bids
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                               qualification['id'],
                                                                                               self.tender_token),
                                           {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, "200 OK")


        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token), {"data": {"status": 'active.pre-qualification.stand-still'}})

        doc_resource = 'documents'
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
            self.tender_id, self.bid_id, doc_resource, self.bid_token), upload_files=[('file', 'name.doc', 'content')],
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (active.pre-qualification.stand-still) tender status")

    def test_put_tender_bidder_document(self):
        doc_id_by_type = {}
        doc_resource = 'documents'
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                              doc_resource, self.bid_token),
                                 upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]
        doc_id_by_type[doc_resource] = {'id': doc_id, 'key': key}

        response = self.app.put('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                doc_resource, doc_id,
                                                                                self.bid_token),
                                status=404,
                                upload_files=[('invalid_name', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.put('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                doc_resource, doc_id,
                                                                                self.bid_token),
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.get('/tenders/{}/bids/{}/{}/{}?{}&acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                   doc_resource, doc_id,
                                                                                   key, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content2')

        response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                doc_resource, doc_id,
                                                                                self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name.doc', response.json["data"]["title"])

        response = self.app.put('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                doc_resource, doc_id,
                                                                                self.bid_token),
                                'content3',
                                content_type='application/msword')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.get('/tenders/{}/bids/{}/{}/{}?{}&acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                   doc_resource, doc_id,
                                                                                   key, self.bid_token))
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

        for doc_resource in ['documents']:
            response = self.app.put('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                    doc_resource, doc_id_by_type[doc_resource]['id'],
                                                                                    self.bid_token),
                                    upload_files=[('file', 'name.doc', 'content4')],
                                    status=403)
            self.assertEqual(response.status, '403 Forbidden')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (active.pre-qualification) tender status")

        # list qualifications
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.assertEqual(response.status, "200 OK")
        # qualify bids
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                               qualification['id'],
                                                                                               self.tender_token),
                                           {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, "200 OK")

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"status": 'active.pre-qualification.stand-still'}})

        doc_resource = 'documents'
        response = self.app.put('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                doc_resource, doc_id_by_type[doc_resource]['id'],
                                                                                self.bid_token),
                                upload_files=[('file', 'name.doc', 'content4')],
                                status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (active.pre-qualification.stand-still) tender status")

    def test_patch_tender_bidder_document(self):
        doc_id_by_type = {}
        doc_resource = 'documents'
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                              doc_resource, self.bid_token),
                                 upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]
        doc_id_by_type[doc_resource] = {'id': doc_id, 'key': key}

        # upload private document
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                              doc_resource, self.bid_token),
                                 upload_files=[('file', 'name_{}_private.doc'.format(doc_resource[:-1]), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}_private.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]
        doc_id_by_type[doc_resource+'private'] = {'id': doc_id, 'key': key}
        response = self.app.patch_json(
            '/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                            doc_resource, doc_id, self.bid_token),
            {"data": {'confidentiality': 'buyerOnly',
                      'confidentialityRationale': 'Only our company sells badgers with pink hair.'}})
        self.assertEqual(response.status, '200 OK')

        doc_resource = 'documents'
        doc_id = doc_id_by_type[doc_resource]['id']
        response = self.app.patch_json('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                       doc_resource, doc_id,
                                                                                       self.bid_token),
                                       {"data": {"documentOf": "lot"}},
                                       status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'relatedItem'},
        ])

        response = self.app.patch_json('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                       doc_resource, doc_id,
                                                                                       self.bid_token),
                                       {"data": {"documentOf": "lot",
                                                 "relatedItem": '0' * 32}},
                                       status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'relatedItem should be one of lots'], u'location': u'body', u'name': u'relatedItem'}
        ])

        response = self.app.patch_json('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                       doc_resource, doc_id,
                                                                                       self.bid_token),
                                       {"data": {"description": "document description", 'language': 'en'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])

        response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                doc_resource, doc_id,
                                                                                self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('document description', response.json["data"]["description"])
        self.assertEqual('en', response.json["data"]["language"])

        # test confidentiality change
        doc_id = doc_id_by_type[doc_resource+'private']['id']
        response = self.app.patch_json('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                       doc_resource, doc_id,
                                                                                       self.bid_token),
                                       {"data": {'confidentiality': 'public',
                                                 'confidentialityRationale': ''}})
        self.assertEqual(response.status, '200 OK')
        response = self.app.patch_json(
            '/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, doc_resource,
                                                            doc_id, self.bid_token),
            {"data": {'confidentiality': 'buyerOnly',
                      'confidentialityRationale': 'Only our company sells badgers with pink hair.'}})
        self.assertEqual(response.status, '200 OK')

        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {'status': 'active.tendering'})
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.app.authorization = auth

        doc_resource = 'documents'
        response = self.app.patch_json('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(
                self.tender_id, self.bid_id, doc_resource, doc_id_by_type[doc_resource]['id'], self.bid_token),
            {"data": {"description": "document description"}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (active.pre-qualification) tender status")

        # list qualifications
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.assertEqual(response.status, "200 OK")
        # qualify bids
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                               qualification['id'],
                                                                                               self.tender_token),
                                           {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, "200 OK")

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"status": 'active.pre-qualification.stand-still'}})
        doc_resource = 'documents'
        response = self.app.patch_json('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                       doc_resource, doc_id_by_type[doc_resource]['id'],
                                                                                       self.bid_token),
                                       {"data": {"description": "document description"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (active.pre-qualification.stand-still) tender status")
        response = self.app.patch_json('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                       doc_resource, doc_id_by_type[doc_resource+'private']['id'],
                                                                                       self.bid_token),
                                       {"data": {"description": "document description"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (active.pre-qualification.stand-still) tender status")

    def test_patch_tender_bidder_document_private(self):
        doc_id_by_type = {}
        private_doc_id_by_type = {}
        doc_resource = 'documents'
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                              doc_resource, self.bid_token),
                                 upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]
        doc_id_by_type[doc_resource] = {'id': doc_id, 'key': key}
        response = self.app.patch_json('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                       doc_resource, doc_id,
                                                                                       self.bid_token),
                                       {"data": {'confidentiality': 'buyerOnly',
                                                 'confidentialityRationale': 'Only our company sells badgers with pink hair.'}
                                        })
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('buyerOnly', response.json["data"]["confidentiality"])
        self.assertEqual('Only our company sells badgers with pink hair.', response.json["data"]["confidentialityRationale"])
        response = self.app.put('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                doc_resource, doc_id,
                                                                                self.bid_token),
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

        self.assertEqual('buyerOnly', response.json["data"]["confidentiality"])
        self.assertEqual('Only our company sells badgers with pink hair.', response.json["data"]["confidentialityRationale"])

    def test_patch_and_put_document_into_invalid_bid(self):
        doc_id_by_type = {}
        doc_resource = 'documents'
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                              doc_resource, self.bid_token),
                                 upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]
        doc_id_by_type[doc_resource] = {'id': doc_id, 'key': key}

        # update tender. we can set value that is less than a value in bids as
        # they will be invalidated by this request
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"value": {'amount': 300.0}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']["value"]["amount"], 300)

        doc_resource = 'documents'
        doc_id = doc_id_by_type[doc_resource]['id']
        response = self.app.patch_json(
            '/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, doc_resource,
                                                            doc_id, self.bid_token),
            {"data": {'confidentiality': 'buyerOnly',
                      'confidentialityRationale': 'Only our company sells badgers with pink hair.'}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document data for 'invalid' bid")
        response = self.app.put('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                doc_resource, doc_id,
                                                                                self.bid_token),
                                'updated',
                                content_type='application/msword', status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in 'invalid' bid")

    def test_download_tender_bidder_document(self):
        doc_id_by_type = {}
        private_doc_id_by_type = {}
        # Create documents of all type
        doc_resource = 'documents'
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                              doc_resource, self.bid_token),
                                 upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]
        private_doc_id_by_type[doc_resource] = {'id': response.json["data"]['id'], 'key': response.json["data"]["url"].split('?')[-1]}

        # make document confidentiality
        response = self.app.patch_json(
            '/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, doc_resource,
                                                            doc_id, self.bid_token),
            {"data": {'confidentiality': 'buyerOnly',
                      'confidentialityRationale': 'Only our company sells badgers with pink hair.'}})
        # Update document
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                              doc_resource, self.bid_token),
                                 upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]
        doc_id_by_type[doc_resource] = {'id': response.json["data"]['id'], 'key': response.json["data"]["url"].split('?')[-1]}

        for container in private_doc_id_by_type, doc_id_by_type:
            # Get document by bid owner
            response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}&{}'.format(
                self.tender_id, self.bid_id, doc_resource,
                container[doc_resource]['id'], self.bid_token, container[doc_resource]['key']))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.body, 'content')
            self.assertEqual(response.headers['Content-Disposition'],  'attachment; filename=name_{}.doc'.format(doc_resource[:-1]))
            self.assertEqual(response.headers['Content-Type'],  'application/msword; charset=UTF-8')

            # Try get bid document by tender owner when tender status is active.tendering
            response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}&{}'.format(self.tender_id, self.bid_id,
                                                                                       doc_resource, container[doc_resource]['id'],
                                                                                       self.tender_token, container[doc_resource]['key']),
                                    status=403)
            self.assertEqual(response.status, '403 Forbidden')
            self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) tender status")

            # Try get bid document by user when tender status is active.tendering
            response = self.app.get('/tenders/{}/bids/{}/{}/{}?{}'.format(self.tender_id, self.bid_id,
                                                                          doc_resource, container[doc_resource]['id'],
                                                                          container[doc_resource]['key']),
                                    status=403)
            self.assertEqual(response.status, '403 Forbidden')
            self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) tender status")

        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        def test_bids_documents_after_tendering_resource(self, doc_id_by_type, private_doc_id_by_type, status):
            doc_resource = 'documents'
            # Get bid document by bid owner when status is {status}
            for container in private_doc_id_by_type, doc_id_by_type:
                response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}&{}'.format(self.tender_id, self.bid_id,
                                                                                           doc_resource, container[doc_resource]['id'],
                                                                                           self.bid_token, container[doc_resource]['key']))
                self.assertEqual(response.status, '200 OK')
                self.assertEqual(response.body, 'content')
                self.assertEqual(response.headers['Content-Disposition'],  'attachment; filename=name_{}.doc'.format(doc_resource[:-1]))
                self.assertEqual(response.headers['Content-Type'],  'application/msword; charset=UTF-8')

            for container in private_doc_id_by_type, doc_id_by_type:
                response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}&{}'.format(self.tender_id, self.bid_id,
                                                                                           'documents', container['documents']['id'],
                                                                                           self.tender_token, container['documents']['key']))
                self.assertEqual(response.status, '200 OK')

        test_bids_documents_after_tendering_resource(self, doc_id_by_type, private_doc_id_by_type, 'active.pre-qualification')

        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.assertEqual(response.status, "200 OK")
        # qualify bids
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                               qualification['id'],
                                                                                               self.tender_token),
                                           {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, "200 OK")

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"status": 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')
        test_bids_documents_after_tendering_resource(self, doc_id_by_type, private_doc_id_by_type, 'active.pre-qualification.stand-still')

    def test_create_tender_bidder_document_nopending(self):
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': test_bids[0]})
        bid = response.json['data']
        token = response.json['access']['token']
        bid_id = bid['id']

        response = self.app.post('/tenders/{}/bids/{}/documents?acc_token={}'.format(self.tender_id, bid_id, token),
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])

        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        # qualify bids
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.app.authorization = ('Basic', ('token', ''))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}'.format(self.tender_id, qualification['id']),
                                           {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, "200 OK")

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"status": 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

    def test_create_tender_bidder_document_description(self):
        doc_id_by_type = {}
        private_doc_id_by_type = {}
        for doc_resource in ['documents']:
            response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                  doc_resource, self.bid_token),
                                     upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            doc_id = response.json["data"]['id']
            self.assertIn(doc_id, response.headers['Location'])
            self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
            key = response.json["data"]["url"].split('?')[-1]
            private_doc_id_by_type[doc_resource] = {'id': response.json["data"]['id'],
                                                    'key': response.json["data"]["url"].split('?')[-1]}

            # make document confidentiality
            response = self.app.patch_json(
                '/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, doc_resource,
                                                                doc_id, self.bid_token),
                {"data": {'confidentiality': 'buyerOnly',
                          "isDescriptionDecision": True}})
            response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                    doc_resource, doc_id,
                                                                                    self.bid_token))
            self.assertEqual(response.json["data"]["confidentiality"], 'buyerOnly')  # Check that document is secret
            self.assertTrue(response.json["data"]["confidentiality"])  # Check if isDescriptionDecision is True

            # Update document
            response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                  doc_resource, self.bid_token),
                                     upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            doc_id = response.json["data"]['id']
            self.assertIn(doc_id, response.headers['Location'])
            self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
            key = response.json["data"]["url"].split('?')[-1]
            doc_id_by_type[doc_resource] = {'id': response.json["data"]['id'],
                                            'key': response.json["data"]["url"].split('?')[-1]}

            for container in private_doc_id_by_type, doc_id_by_type:
                # Get document by bid owner
                response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}&{}'.format(
                    self.tender_id, self.bid_id, doc_resource,
                    container[doc_resource]['id'], self.bid_token, container[doc_resource]['key']))
                self.assertEqual(response.status, '200 OK')
                self.assertEqual(response.body, 'content')
                self.assertEqual(response.headers['Content-Disposition'],
                                 'attachment; filename=name_{}.doc'.format(doc_resource[:-1]))
                self.assertEqual(response.headers['Content-Type'], 'application/msword; charset=UTF-8')

                # Try get bid document by tender owner when tender status is active.tendering
                response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}&{}'.format(self.tender_id, self.bid_id, doc_resource,
                                                                                           container[doc_resource]['id'],
                                                                                           self.tender_token, container[doc_resource]['key']),
                                        status=403)
                self.assertEqual(response.status, '403 Forbidden')
                self.assertEqual(response.json['errors'][0]["description"],
                                 "Can't view bid document in current (active.tendering) tender status")

                # Try get bid document by user when tender status is active.tendering
                response = self.app.get('/tenders/{}/bids/{}/{}/{}?{}'.format(self.tender_id, self.bid_id, doc_resource,
                                                                              container[doc_resource]['id'], container[doc_resource]['key']),
                                        status=403)
                self.assertEqual(response.status, '403 Forbidden')
                self.assertEqual(response.json['errors'][0]["description"],
                                 "Can't view bid document in current (active.tendering) tender status")

    def test_create_tender_bidder_invalid_document_description(self):
        doc_id_by_type = {}
        private_doc_id_by_type = {}
        doc_resource = 'documents'
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                              doc_resource, self.bid_token),
                                 upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]
        private_doc_id_by_type[doc_resource] = {'id': response.json["data"]['id'],
                                                'key': response.json["data"]["url"].split('?')[-1]}

        # make document confidentiality
        response = self.app.patch_json(
            '/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, doc_resource,
                                                            doc_id, self.bid_token),
            {"data": {'confidentiality': 'buyerOnly',
                      "isDescriptionDecision": False}}, status=422)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json["errors"][0]["description"][0], "confidentialityRationale is required")
        # Update document
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                              doc_resource, self.bid_token),
                                 upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual(response.json["data"]["confidentiality"], 'public')
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]
        doc_id_by_type[doc_resource] = {'id': response.json["data"]['id'],
                                        'key': response.json["data"]["url"].split('?')[-1]}

        for container in private_doc_id_by_type, doc_id_by_type:
            # Get document by bid owner
            response = self.app.get(
                '/tenders/{}/bids/{}/{}/{}?acc_token={}&{}'.format(self.tender_id, self.bid_id,
                                                                   doc_resource, container[doc_resource]['id'],
                                                                   self.bid_token, container[doc_resource]['key']))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.body, 'content')
            self.assertEqual(response.headers['Content-Disposition'],
                             'attachment; filename=name_{}.doc'.format(doc_resource[:-1]))
            self.assertEqual(response.headers['Content-Type'], 'application/msword; charset=UTF-8')

            # Try get bid document by tender owner when tender status is active.tendering
            response = self.app.get(
                '/tenders/{}/bids/{}/{}/{}?acc_token={}&{}'.format(self.tender_id, self.bid_id, doc_resource,
                                                                   container[doc_resource]['id'],
                                                                   self.tender_token,
                                                                   container[doc_resource]['key']),
                status=403)
            self.assertEqual(response.status, '403 Forbidden')
            self.assertEqual(response.json['errors'][0]["description"],
                             "Can't view bid document in current (active.tendering) tender status")

            # Try get bid document by user when tender status is active.tendering
            response = self.app.get('/tenders/{}/bids/{}/{}/{}?{}'.format(self.tender_id, self.bid_id, doc_resource,
                                                                          container[doc_resource]['id'],
                                                                          container[doc_resource]['key']),
                                    status=403)
            self.assertEqual(response.status, '403 Forbidden')
            self.assertEqual(response.json['errors'][0]["description"],
                             "Can't view bid document in current (active.tendering) tender status")

    def test_create_tender_bidder_invalid_confidential_document(self):
        private_doc_id_by_type = {}
        doc_resource = 'documents'
        response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                              doc_resource, self.bid_token),
                                 upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name_{}.doc'.format(doc_resource[:-1]), response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]
        private_doc_id_by_type[doc_resource] = {'id': response.json["data"]['id'],
                                                'key': response.json["data"]["url"].split('?')[-1]}

        # make document confidentiality
        response = self.app.patch_json(
            '/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id, doc_resource,
                                                            doc_id, self.bid_token),
            {"data": {'confidentiality': 'buyerOnly',
                      'confidentialityRationale': 'To small field'}}, status=422)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json["errors"][0]["description"][0], "confidentialityRationale should contain at least 30 characters")
        # Get document
        response = self.app.get('/tenders/{}/bids/{}/{}/{}?acc_token={}'.format(self.tender_id, self.bid_id,
                                                                                doc_resource, doc_id,
                                                                                self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json["data"]["confidentiality"], 'public')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CompetitiveDialogEUBidResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogEUBidFeaturesResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogEUBidDocumentResourceTest))

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')