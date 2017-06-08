# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest,
    test_bids,
    test_lots,
    author

)

test_tender_bids = deepcopy(test_bids[:2])
for test_bid in test_tender_bids:
    test_bid['tenderers'] = [author]


class TenderStage2EUAwardResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = 'active.tendering'
    initial_bids = test_tender_bids
    initial_lots = test_lots
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        """ Create tender with lots add 2 bids, play auction and get award """
        super(TenderStage2EUAwardResourceTest, self).setUp()
        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {'id': self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        # qualify bids
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.app.authorization = ('Basic', ('broker', ''))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
                self.tender_id, qualification['id'], self.tender_token),
                {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
            self.assertEqual(response.status, '200 OK')

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {'data': {'status': 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        # switch to active.auction time
        self.set_status('active.auction', {'id': self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.auction')

        # switch to auction role
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        for lot_id in self.lots:
            response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id['id']),
                                          {'data': {'bids': auction_bids_data}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], 'active.qualification')
        
        # get award
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.award_id = response.json['data'][0]['id']
        self.bid_token = self.initial_bids_tokens[self.bids[0]['id']]
        self.app.authorization = ('Basic', ('broker', ''))
    
    def test_create_tender_award_invalid(self):
        """ Test create tender award with invalid data """
        self.app.authorization = ('Basic', ('token', ''))
        request_path = '/tenders/{}/awards'.format(self.tender_id)
        response = self.app.post(request_path, 'data', status=415)
        self.assertEqual(response.status, '415 Unsupported Media Type')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description':
                u"Content-Type header should be one of ['application/json']",
             u'location': u'header',
             u'name': u'Content-Type'}
        ])

        response = self.app.post(request_path, 'data', content_type='application/json', status=422)
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

        response = self.app.post_json(request_path, {'data': {'invalid_field': 'invalid_value'}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Rogue field', u'location':
                u'body', u'name': u'invalid_field'}
        ])

        response = self.app.post_json(request_path,
                                      {'data': {'suppliers': [{'identifier': 'invalid_value'}]}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': {u'identifier': [
                u'Please use a mapping for this field or Identifier instance instead of unicode.']},
                u'location': u'body',
                u'name': u'suppliers'}
        ])

        response = self.app.post_json(request_path, {
                                      'data': {'suppliers': [{'identifier': {'id': 0}}]}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'contactPoint': [u'This field is required.'],
                               u'identifier': {u'scheme': [u'This field is required.']},
                               u'name': [u'This field is required.'],
                               u'address': [u'This field is required.']}],
             u'location': u'body', u'name': u'suppliers'},
            {u'description': [u'This field is required.'],
             u'location': u'body', u'name': u'bid_id'}
        ])

        response = self.app.post_json(request_path,
                                      {'data': {'suppliers': [{'name': 'name',
                                                               'identifier': {'uri': 'invalid_value'}}]}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'contactPoint': [u'This field is required.'],
                               u'identifier': {u'scheme': [u'This field is required.'],
                                               u'id': [u'This field is required.'],
                                               u'uri': [u'Not a well formed URL.']},
                               u'address': [u'This field is required.']}],
             u'location': u'body', u'name': u'suppliers'},
            {u'description': [u'This field is required.'],
             u'location': u'body', u'name': u'bid_id'}
        ])

        response = self.app.post_json(request_path,
                                      {'data': {'suppliers': [author],
                                                'status': 'pending',
                                                'bid_id': self.bids[0]['id'],
                                                'lotID': '0' * 32}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'lotID should be one of lots'], u'location': u'body', u'name': u'lotID'}
        ])

        response = self.app.post_json('/tenders/some_id/awards',
                                      {'data': {'suppliers': [author],
                                                'bid_id': self.bids[0]['id']}},
                                      status=404)
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

        bid = self.bids[0]
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author],
                                                'status': 'pending',
                                                'bid_id': self.bids[0]['id'],
                                                'lotID': bid['lotValues'][0]['relatedLot']}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't create award in current (complete) tender status")

    def test_create_tender_award(self):
        """ Test create tender award """
        # Set tender award status to active
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id,
                                                                                   self.award_id,
                                                                                   self.tender_token),
                                       {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'active')

        # check tender status
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'active.awarded')

        # set award status to cancelled
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token),
            {'data': {'status': 'cancelled'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'cancelled')
        self.assertIn('Location', response.headers)

    def test_patch_tender_award(self):
        """ Test patch tender award """
        # Try set award to unsuccessful, by bad award id
        response = self.app.patch_json('/tenders/{}/awards/some_id'.format(self.tender_id),
                                       {'data': {'status': 'unsuccessful'}},
                                       status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        # Try set award to unsuccessful by bad tender id
        response = self.app.patch_json('/tenders/some_id/awards/some_id',
                                       {'data': {'status': 'unsuccessful'}},
                                       status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        # Try set field awardStatus to unsuccessful
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token),
            {'data': {'awardStatus': 'unsuccessful'}},
            status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'], [
            {'location': 'body', 'name': 'awardStatus', 'description': 'Rogue field'}
        ])

        # Set award to unsuccessful
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token),
            {'data': {'status': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)
        new_award_location = response.headers['Location']

        # Try set award to pending
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token),
            {'data': {'status': 'pending'}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't update award in current (unsuccessful) status")

        # Check awards length and get new award id
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 2)
        self.assertIn(response.json['data'][1]['id'], new_award_location)
        new_award = response.json['data'][-1]

        # Set award status to active
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, new_award['id'], self.tender_token),
            {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

        # check awards length
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 2)

        # cancel second award
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, new_award['id'], self.tender_token),
            {'data': {'status': 'cancelled'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)

        # check awards length
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 3)

        # set tender satus to complete
        self.set_status('complete')

        # check award value
        response = self.app.get('/tenders/{}/awards/{}'.format(self.tender_id, self.award_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['value']['amount'], 469.0)

        # try change award when tender status is complete
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token),
            {'data': {'status': 'unsuccessful'}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't update award in current (complete) tender status")

    def test_patch_tender_award_active(self):
        """ Test patching tender award in status active """
        # Set award status to unsuccessful
        request_path = '/tenders/{}/awards'.format(self.tender_id)
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token),
            {'data': {'status': 'unsuccessful'}})

        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)
        new_award_location = response.headers['Location']

        # Set award to status active
        response = self.app.patch_json(new_award_location[-81:]+'?acc_token={}'.format(self.tender_token),
                                       {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertNotIn('Location', response.headers)

        # check awards length
        response = self.app.get(request_path)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 2)

        # create complaint on award
        response = self.app.post_json(new_award_location[-81:]+'/complaints?acc_token={}'.format(self.bid_token),
                                      {'data': {'title': 'complaint title',
                                                'description': 'complaint description',
                                                'author': author,
                                                'status': 'pending'}})
        self.assertEqual(response.status, '201 Created')

        # switch to reviewer and set complaint status to accepted
        self.app.authorization = ('Basic', ('reviewer', ''))
        response = self.app.patch_json(new_award_location[-81:]+'/complaints/{}'.format(response.json['data']['id']),
                                       {'data': {'status': 'accepted'}})
        self.assertEqual(response.status, '200 OK')

        # set complaint status to satisfied
        response = self.app.patch_json(new_award_location[-81:]+'/complaints/{}'.format(response.json['data']['id']),
                                       {'data': {'status': 'satisfied'}})
        self.assertEqual(response.status, '200 OK')

        # switch to broker and create another complaint
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('{}/complaints?acc_token={}'.format(new_award_location[-81:], self.bid_token),
                                      {'data': {'title': 'complaint title',
                                                'description': 'complaint description',
                                                'author': author}})
        self.assertEqual(response.status, '201 Created')

        # and set award cancelled
        response = self.app.patch_json(new_award_location[-81:]+'?acc_token={}'.format(self.tender_token),
                                       {'data': {'status': 'cancelled'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)
        new_award_location = response.headers['Location']

        # make awards unsuccessful
        response = self.app.patch_json(new_award_location[-81:]+'?acc_token={}'.format(self.tender_token),
                                       {'data': {'status': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)
        new_award_location = response.headers['Location']

        # make another award unsuccessful
        response = self.app.patch_json(new_award_location[-81:]+'?acc_token={}'.format(self.tender_token),
                                       {'data': {'status': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertNotIn('Location', response.headers)

        # check length of awards
        response = self.app.get(request_path)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 4)

    def test_patch_tender_award_unsuccessful(self):
        request_path = '/tenders/{}/awards'.format(self.tender_id)
        # make award unsuccessful
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token),
            {'data': {'status': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)
        new_award_location = response.headers['Location']
        # get new award
        response = self.app.patch_json(new_award_location[-81:]+'?acc_token={}'.format(self.tender_token),
                                       {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertNotIn('Location', response.headers)

        # check awards length
        response = self.app.get(request_path)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 2)

        # create complaint on award
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title',
                      'description': 'complaint description',
                      'author': author,
                      'status': 'pending'}})
        self.assertEqual(response.status, '201 Created')

        # set status complaint to accepted by reviewer
        self.app.authorization = ('Basic', ('reviewer', ''))
        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(
            self.tender_id, self.award_id, response.json['data']['id']),
            {'data': {'status': 'accepted'}})
        self.assertEqual(response.status, '200 OK')

        # set status complaint to satisfied by reviewer
        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(
            self.tender_id, self.award_id, response.json['data']['id']),
            {'data': {'status': 'satisfied'}})
        self.assertEqual(response.status, '200 OK')

        # create complaint by broker
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('{}/complaints?acc_token={}'.format(new_award_location[-81:], self.bid_token),
                                      {'data': {'title': 'complaint title',
                                                'description': 'complaint description',
                                                'author': author}})
        self.assertEqual(response.status, '201 Created')

        # set award status to cancelled by broker
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token),
            {'data': {'status': 'cancelled'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)
        new_award_location = response.headers['Location']

        # set new award status to unsuccessful by broker and get another new award location
        response = self.app.patch_json(new_award_location[-81:]+'?acc_token={}'.format(self.tender_token),
                                       {'data': {'status': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)
        new_award_location = response.headers['Location']

        # set new award status to unseccessful by broker
        response = self.app.patch_json(new_award_location[-81:]+'?acc_token={}'.format(self.tender_token),
                                       {'data': {'status': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertNotIn('Location', response.headers)

        # check that awards length is 4
        response = self.app.get(request_path)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 4)

    def test_get_tender_award(self):
        """ Test get award """
        # get award by tender id and award id
        response = self.app.get('/tenders/{}/awards/{}'.format(self.tender_id, self.award_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertTrue(response.json['data'])

        # try get award by bad award id
        response = self.app.get('/tenders/{}/awards/some_id'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        # try get award by bad tender id
        response = self.app.get('/tenders/some_id/awards/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

    def test_patch_tender_award_Administrator_change(self):

        # create award
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author],
                                                'status': 'pending',
                                                'bid_id': self.bids[0]['id'],
                                                'lotID': self.lots[0]['id']}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        award = response.json['data']
        complaintPeriod = award['complaintPeriod'][u'startDate']

        # change complaintPeriod.endDate by administrator
        self.app.authorization = ('Basic', ('administrator', ''))
        response = self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, award['id']),
                                       {'data': {'complaintPeriod': {'endDate': award['complaintPeriod'][u'startDate']}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('endDate', response.json['data']['complaintPeriod'])
        self.assertEqual(response.json['data']['complaintPeriod']['endDate'], complaintPeriod)


class TenderStage2EULotAwardResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = 'active.tendering'
    initial_bids = test_tender_bids
    initial_lots = test_lots
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderStage2EULotAwardResourceTest, self).setUp()
        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {'id': self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        # qualify bids
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.app.authorization = ('Basic', ('broker', ''))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
                self.tender_id, qualification['id'], self.tender_token),
                {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
            self.assertEqual(response.status, '200 OK')

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
            self.tender_id, self.tender_token),
            {'data': {'status': 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        # switch to active.auction
        self.set_status('active.auction', {'id': self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.auction')
        
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        for lot_id in self.lots:
            response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id['id']),
                                          {'data': {'bids': auction_bids_data}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], 'active.qualification')
        
        # Get award
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.award_id = response.json['data'][0]['id']
        self.bid_token = self.initial_bids_tokens[self.bids[0]['id']]
        self.app.authorization = ('Basic', ('broker', ''))

    def test_create_tender_award(self):
        """ Test create tender award """
        # switch to role token, and try create award
        self.app.authorization = ('Basic', ('token', ''))
        request_path = '/tenders/{}/awards'.format(self.tender_id)
        response = self.app.post_json(request_path,
                                      {'data': {'suppliers': [author],
                                                'status': 'pending', 'bid_id': self.bids[0]['id']}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'], [
            {'location': 'body', 'name': 'lotID', 'description': ['This field is required.']}
        ])

        # create award
        response = self.app.post_json(request_path, {'data': {'suppliers': [author],
                                                              'status': 'pending',
                                                              'bid_id': self.bids[0]['id'],
                                                              'lotID': self.lots[0]['id']}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        award = response.json['data']
        self.assertEqual(award['suppliers'][0]['name'], author['name'])
        self.assertEqual(award['lotID'], self.lots[0]['id'])
        self.assertIn('id', award)
        self.assertIn(award['id'], response.headers['Location'])

        # switch to broker and check award witch we create before
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get(request_path)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'][-1], award)

        # set award status to active
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, award['id'], self.tender_token),
            {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'active')

        # check tender status
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'active.awarded')

        # cancel award
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, award['id'], self.tender_token), {'data': {'status': 'cancelled'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'cancelled')
        self.assertIn('Location', response.headers)

    def test_patch_tender_award(self):
        """ Test patch tender award """
        # try set award status to unsuccessful, by bad award id
        response = self.app.patch_json('/tenders/{}/awards/some_id'.format(self.tender_id),
                                       {'data': {'status': 'unsuccessful'}},
                                       status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        # try set award status to unsuccessful, by bad tender id
        response = self.app.patch_json('/tenders/some_id/awards/some_id', {'data': {'status': 'unsuccessful'}},
                                       status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        # try set award to awardStatus
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token),
            {'data': {'awardStatus': 'unsuccessful'}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'], [
            {'location': 'body', 'name': 'awardStatus', 'description': 'Rogue field'}
        ])

        # set award status to unsuccessful
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token), {'data': {'status': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)
        new_award_location = response.headers['Location']

        # try update award when status is unsuccessful
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token), {'data': {'status': 'pending'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't update award in current (unsuccessful) status")

        # get new award
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 2)
        self.assertIn(response.json['data'][-1]['id'], new_award_location)
        new_award = response.json['data'][-1]

        # set new award to active
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, new_award['id'], self.tender_token), {'data': {'status': 'active', 'eligible': True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

        # check awards lenght
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 2)

        # cancelled second award
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, new_award['id'], self.tender_token), {'data': {'status': 'cancelled'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)

        # check awards length
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 3)

        self.set_status('complete')

        # check award amount when tender status is complete
        response = self.app.get('/tenders/{}/awards/{}'.format(self.tender_id, self.award_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['value']['amount'], 469.0)

        # try set award status when tender status is complete
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token), {'data': {'status': 'unsuccessful'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't update award in current (complete) tender status")

    def test_patch_tender_award_unsuccessful(self):
        request_path = '/tenders/{}/awards'.format(self.tender_id)
        # make award unsuccessful and get new
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token), {'data': {'status': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)
        new_award_location = response.headers['Location']

        # make award active
        response = self.app.patch_json(new_award_location[-81:]+'?acc_token={}'.format(self.tender_token),
                                       {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertNotIn('Location', response.headers)

        # check award length
        response = self.app.get(request_path)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 2)

        # create complaint by user
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title',
                      'description': 'complaint description',
                      'author': author,
                      'status': 'pending'}})
        self.assertEqual(response.status, '201 Created')

        # switch to reviewer role and make complaint status accepted
        self.app.authorization = ('Basic', ('reviewer', ''))
        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, response.json['data']['id'], self.bid_token),
            {'data': {'status': 'accepted'}})
        self.assertEqual(response.status, '200 OK')

        # set complaint status to satisfied
        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, response.json['data']['id'], self.bid_token),
            {'data': {'status': 'satisfied'}})
        self.assertEqual(response.status, '200 OK')

        # switch to broker role and add another complaint
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('{}/complaints?acc_token={}'.format(new_award_location[-81:], self.bid_token),
                                      {'data': {'title': 'complaint title',
                                                'description': 'complaint description',
                                                'author': author}})
        self.assertEqual(response.status, '201 Created')

        # set ward status to cancelled and get another
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token), {'data': {'status': 'cancelled'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)
        new_award_location = response.headers['Location']

        # set another award to unsuccessful
        response = self.app.patch_json(new_award_location[-81:]+'?acc_token={}'.format(self.tender_token),
                                       {'data': {'status': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)
        new_award_location = response.headers['Location']

        # set another award to unsuccessful
        response = self.app.patch_json(new_award_location[-81:]+'?acc_token={}'.format(self.tender_token),
                                       {'data': {'status': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertNotIn('Location', response.headers)

        # check awards length
        response = self.app.get(request_path)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 4)


class TenderStage2EU2LotAwardResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = 'active.tendering'
    initial_lots = deepcopy(2 * test_lots)
    initial_bids = test_tender_bids
    initial_auth = ('Basic', ('broker', ''))
    
    def setUp(self):
        super(TenderStage2EU2LotAwardResourceTest, self).setUp()
        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {'id': self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        # qualify bids
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.app.authorization = ('Basic', ('broker', ''))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
                self.tender_id, qualification['id'], self.tender_token),
                {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
            self.assertEqual(response.status, '200 OK')

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'status': 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        # switch to active.auction
        self.set_status('active.auction', {'id': self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.auction')

        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        for lot_id in self.lots:
            response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id['id']),
                                          {'data': {'bids': auction_bids_data}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], 'active.qualification')

        # Get award
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.award_id = response.json['data'][0]['id']
        self.app.authorization = ('Basic', ('broker', ''))

    def test_create_tender_award(self):
        request_path = '/tenders/{}/awards'.format(self.tender_id)
        # cancel lot
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
            self.tender_id, self.tender_token),
            {'data': {'reason': 'cancellation reason',
                      'status': 'active',
                      'cancellationOf': 'lot',
                      'relatedLot': self.lots[0]['id']
        }})
        self.assertEqual(response.status, '201 Created')

        # try switch role to token and try create award on canceled lot
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json(request_path,
                                      {'data': {'suppliers': [author],
                                                'status': 'pending',
                                                'bid_id': self.bids[0]['id'],
                                                'lotID': self.lots[0]['id']}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can create award only in active lot status')

        # create award on lot
        response = self.app.post_json(request_path, {'data': {'suppliers': [author],
                                                              'status': 'pending',
                                                              'bid_id': self.bids[0]['id'],
                                                              'lotID': self.lots[1]['id']}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        award = response.json['data']
        self.assertEqual(award['suppliers'][0]['name'], author['name'])
        self.assertEqual(award['lotID'], self.lots[1]['id'])
        self.assertIn('id', award)
        self.assertIn(award['id'], response.headers['Location'])

        # get award
        response = self.app.get(request_path)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'][-1], award)

        # make award active
        response = self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, award['id']),
                                       {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'active')

        # check tender status
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'active.awarded')

        # cancel award
        response = self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, award['id']),
                                       {'data': {'status': 'cancelled'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'cancelled')
        self.assertIn('Location', response.headers)

    def test_patch_tender_award(self):
        # set award status to active
        request_path = '/tenders/{}/awards'.format(self.tender_id)
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token),
            {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

        # check awards length
        response = self.app.get(request_path)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 2)
        new_award = response.json['data'][-1]

        # cancel tender
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason',
                                                          'status': 'active',
                                                          'cancellationOf': 'lot',
                                                          'relatedLot': self.lots[1]['id']
        }})
        self.assertEqual(response.status, '201 Created')

        # try set award on cancel tender
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, new_award['id'], self.tender_token),
            {'data': {'status': 'unsuccessful'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can update award only in active lot status')


class TenderStage2EUAwardComplaintResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = 'active.tendering'
    initial_bids = test_tender_bids
    initial_lots = deepcopy(2 * test_lots)
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderStage2EUAwardComplaintResourceTest, self).setUp()
        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {'id': self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        # qualify bids
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.app.authorization = ('Basic', ('broker', ''))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
                self.tender_id, qualification['id'], self.tender_token),
                {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
            self.assertEqual(response.status, '200 OK')

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {'data': {'status': 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        # switch to active.auction
        self.set_status('active.auction', {'id': self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.auction')

        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        for lot_id in self.lots:
            response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id['id']),
                                          {'data': {'bids': auction_bids_data}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], 'active.qualification')

        # Get award
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.award_id = response.json['data'][0]['id']
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token), {'data': {'status': 'active', "qualified": True, "eligible": True}})
        self.bid_token = self.initial_bids_tokens[self.bids[0]['id']]
        self.app.authorization = ('Basic', ('broker', ''))

    def test_create_tender_award_complaint_invalid(self):
        response = self.app.post_json('/tenders/some_id/awards/some_id/complaints',
                                      {'data': {'title': 'complaint title',
                                                'description': 'complaint description',
                                                'author': author}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}
        ])

        request_path = '/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token)

        response = self.app.post(request_path, 'data', status=415)
        self.assertEqual(response.status, '415 Unsupported Media Type')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description':
                u"Content-Type header should be one of ['application/json']",
             u'location': u'header',
             u'name': u'Content-Type'}
        ])

        response = self.app.post(request_path, 'data', content_type='application/json', status=422)
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

        response = self.app.post_json(request_path, {'data': {}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'author'},
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'title'},
        ])

        response = self.app.post_json(request_path, {'data': {'invalid_field': 'invalid_value'}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Rogue field', u'location':
                u'body', u'name': u'invalid_field'}
        ])

        response = self.app.post_json(request_path, {'data': {'author': {'identifier': 'invalid_value'}}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': {u'identifier': [
                u'Please use a mapping for this field or Identifier instance instead of unicode.']},
                u'location': u'body',
                u'name': u'author'}
        ])

        response = self.app.post_json(request_path, {'data': {'title': 'complaint title',
                                                              'description': 'complaint description',
                                                              'author': {'identifier': {'id': 0}}}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': {u'contactPoint': [u'This field is required.'],
                              u'identifier': {u'scheme': [u'This field is required.']},
                              u'name': [u'This field is required.'],
                              u'address': [u'This field is required.']},
             u'location': u'body', u'name': u'author'}
        ])

        response = self.app.post_json(request_path, {'data': {'title': 'complaint title',
                                                              'description': 'complaint description',
                                                              'author': {'name': 'name',
                                                                         'identifier': {'uri': 'invalid_value'}}}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': {u'contactPoint': [u'This field is required.'],
                              u'identifier': {u'scheme': [u'This field is required.'],
                                              u'id': [u'This field is required.'],
                                              u'uri': [u'Not a well formed URL.']},
                              u'address': [u'This field is required.']},
             u'location': u'body', u'name': u'author'}
        ])

    def test_create_tender_award_complaint(self):
        # create complaint
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title',
                      'description': 'complaint description',
                      'author': author,
                      'status': 'pending'}})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']
        self.assertEqual(complaint['author']['name'], author['name'])
        self.assertIn('id', complaint)
        self.assertIn(complaint['id'], response.headers['Location'])

        self.set_status('active.awarded')

        # check tender status
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'active.awarded')

        self.set_status('unsuccessful')
        # try add complaint to unsuccessful tender
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title',
                      'description': 'complaint description',
                      'author': author}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't add complaint in current (unsuccessful) tender status")

    def test_patch_tender_award_complaint(self):
        # create complaint on award
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title',
                      'description': 'complaint description',
                      'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']
        owner_token = response.json['access']['token']

        # try cancel complaint by tender owner
        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, complaint['id'], self.tender_token),
            {'data': {'status': 'cancelled', 'cancellationReason': 'reason'}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Forbidden')

        # set award to status active
        #response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            #self.tender_id, self.award_id, self.tender_token),
            #{'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        #self.assertEqual(response.status, '200 OK')
        #self.assertEqual(response.content_type, 'application/json')
        #self.assertEqual(response.json['data']['status'], 'active')

        # patch complaint
        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, complaint['id'], owner_token),
            {'data': {'title': 'claim title'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['title'], 'claim title')

        # set complaints to status pending
        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, complaint['id'], owner_token),
            {'data': {'status': 'pending'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'pending')

        # set complaint status to stopping
        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, complaint['id'], owner_token),
            {'data': {'status': 'stopping', 'cancellationReason': 'reason'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'stopping')
        self.assertEqual(response.json['data']['cancellationReason'], 'reason')

        # try patch complaint with bad id
        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/some_id'.format(self.tender_id, self.award_id),
                                       {'data': {'status': 'resolved', 'resolution': 'resolution text'}},
                                       status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'complaint_id'}
        ])

        # try patch complaint with bad tender id
        response = self.app.patch_json('/tenders/some_id/awards/some_id/complaints/some_id',
                                       {'data': {'status': 'resolved', 'resolution': 'resolution text'}},
                                       status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        # try set complaint status by tender owner
        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, complaint['id'], owner_token),
            {'data': {'status': 'cancelled', 'cancellationReason': 'reason'}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], "Can't update complaint")

        # try patch complaint by bad award id
        response = self.app.patch_json('/tenders/{}/awards/some_id/complaints/some_id'.format(self.tender_id),
                                       {'data': {'status': 'resolved', 'resolution': 'resolution text'}},
                                       status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        # get award complaint
        response = self.app.get('/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id,
                                                                             self.award_id,
                                                                             complaint['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'stopping')
        self.assertEqual(response.json['data']['cancellationReason'], 'reason')
        # create another omplaint
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']
        owner_token = response.json['access']['token']

        self.set_status('complete')

        # try patch complaint when tender status is complete
        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, complaint['id'], owner_token),
            {'data': {'status': 'claim'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't update complaint in current (complete) tender status")

    def test_review_tender_award_complaint(self):
        # try create complaint in different statuses
        for status in ['invalid', 'declined', 'satisfied']:
            self.app.authorization = ('Basic', ('token', ''))
            response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
                self.tender_id, self.award_id, self.bid_token),
                {'data': {'title': 'complaint title',
                          'description': 'complaint description',
                          'author': author,
                          'status': 'pending'}})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            complaint = response.json['data']

            self.app.authorization = ('Basic', ('reviewer', ''))
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(
                self.tender_id, self.award_id, complaint['id']),
                {'data': {'decision': '{} complaint'.format(status)}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.json['data']['decision'], '{} complaint'.format(status))

            if status != 'invalid':
                response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(
                    self.tender_id, self.award_id, complaint['id']),
                    {'data': {'status': 'accepted'}})
                self.assertEqual(response.status, '200 OK')
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.json['data']['status'], 'accepted')

                response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(
                    self.tender_id, self.award_id, complaint['id']),
                    {'data': {'decision': 'accepted:{} complaint'.format(status)}})
                self.assertEqual(response.status, '200 OK')
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.json['data']['decision'], 'accepted:{} complaint'.format(status))

            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(
                self.tender_id, self.award_id, complaint['id']),
                {'data': {'status': status}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.json['data']['status'], status)

    def test_get_tender_award_complaint(self):
        """ Test create complaint and try get """
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}'.format(
            self.tender_id, self.award_id, complaint['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], complaint)

        response = self.app.get('/tenders/{}/awards/{}/complaints/some_id'.format(self.tender_id, self.award_id),
                                status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'complaint_id'}
        ])

        response = self.app.get('/tenders/some_id/awards/some_id/complaints/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

    def test_get_tender_award_complaints(self):
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']

        response = self.app.get('/tenders/{}/awards/{}/complaints'.format(self.tender_id, self.award_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'][0], complaint)

        response = self.app.get('/tenders/some_id/awards/some_id/complaints', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': author}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can add complaint only in complaintPeriod')


class TenderStage2EULotAwardComplaintResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = 'active.tendering'
    initial_lots = deepcopy(test_lots)
    initial_bids = test_tender_bids
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderStage2EULotAwardComplaintResourceTest, self).setUp()

        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {'id': self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        # qualify bids
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.app.authorization = ('Basic', ('broker', ''))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
                self.tender_id, qualification['id'], self.tender_token),
                {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
            self.assertEqual(response.status, '200 OK')

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {'data': {'status': 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        # switch to active.auction
        self.set_status('active.auction', {'id': self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.auction')

        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        for lot_id in self.lots:
            response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id['id']),
                                          {'data': {'bids': auction_bids_data}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], 'active.qualification')

        # Create award
        self.app.authorization = ('Basic', ('token', ''))
        bid = self.bids[0]
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author],
                                                'status': 'pending',
                                                'bid_id': bid['id'],
                                                'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, self.award_id), {'data': {'status': 'active', "qualified": True, "eligible": True}})
        self.bid_token = self.initial_bids_tokens[self.bids[0]['id']]
        self.app.authorization = ('Basic', ('broker', ''))

    def test_create_tender_award_complaint(self):
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token), {'data': {'title': 'complaint title',
                                                                      'description': 'complaint description',
                                                                      'author': author,
                                                                      'status': 'pending'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']
        self.assertEqual(complaint['author']['name'], author['name'])
        self.assertIn('id', complaint)
        self.assertIn(complaint['id'], response.headers['Location'])

        self.set_status('active.awarded')

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'active.awarded')

        self.set_status('unsuccessful')

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title',
                      'description': 'complaint description',
                      'author': author}}, status=403)

        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't add complaint in current (unsuccessful) tender status")

    def test_patch_tender_award_complaint(self):
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token), {'data': {'title': 'complaint title',
                                                                      'description': 'complaint description',
                                                                      'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']
        owner_token = response.json['access']['token']

        #response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            #self.tender_id, self.award_id, self.tender_token),
            #{'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        #self.assertEqual(response.status, '200 OK')
        #self.assertEqual(response.content_type, 'application/json')
        #self.assertEqual(response.json['data']['status'], 'active')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, complaint['id'], owner_token), {'data': {'status': 'pending'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'pending')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, complaint['id'], owner_token),
            {'data': {'status': 'stopping', 'cancellationReason': 'reason'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'stopping')
        self.assertEqual(response.json['data']['cancellationReason'], 'reason')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/some_id'.format(self.tender_id, self.award_id),
                                       {'data': {'status': 'resolved', 'resolution': 'resolution text'}},
                                       status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'complaint_id'}
        ])

        response = self.app.patch_json('/tenders/some_id/awards/some_id/complaints/some_id',
                                       {'data': {'status': 'resolved', 'resolution': 'resolution text'}},
                                       status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, complaint['id'], owner_token),
            {'data': {'status': 'cancelled', 'cancellationReason': 'reason'}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], "Can't update complaint")

        response = self.app.patch_json('/tenders/{}/awards/some_id/complaints/some_id'.format(self.tender_id),
                                       {'data': {'status': 'resolved', 'resolution': 'resolution text'}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id,
                                                                             self.award_id,
                                                                             complaint['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'stopping')
        self.assertEqual(response.json['data']['cancellationReason'], 'reason')

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title',
                      'description': 'complaint description',
                      'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']
        owner_token = response.json['access']['token']

        self.set_status('complete')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, complaint['id'], owner_token), {'data': {'status': 'claim'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't update complaint in current (complete) tender status")

    def test_get_tender_award_complaint(self):
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title',
                      'description': 'complaint description',
                      'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id,
                                                                             self.award_id,
                                                                             complaint['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], complaint)

        response = self.app.get('/tenders/{}/awards/{}/complaints/some_id'.format(self.tender_id, self.award_id),
                                status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'complaint_id'}
        ])

        response = self.app.get('/tenders/some_id/awards/some_id/complaints/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

    def test_get_tender_award_complaints(self):
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title',
                      'description': 'complaint description',
                      'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']

        response = self.app.get('/tenders/{}/awards/{}/complaints'.format(self.tender_id, self.award_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'][0], complaint)

        response = self.app.get('/tenders/some_id/awards/some_id/complaints', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title',
                      'description': 'complaint description',
                      'author': author}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can add complaint only in complaintPeriod')


class TenderStage2EU2LotAwardComplaintResourceTest(TenderStage2EULotAwardComplaintResourceTest):
    initial_lots = deepcopy(2 * test_lots)

    def test_create_tender_award_complaint(self):
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title', 'description': 'complaint description',
                      'author': author, 'status': 'pending'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']
        self.assertEqual(complaint['author']['name'], author['name'])
        self.assertIn('id', complaint)
        self.assertIn(complaint['id'], response.headers['Location'])

        self.set_status('active.awarded')

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'active.awarded')

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'active',
                                                'cancellationOf': 'lot',
                                                'relatedLot': self.lots[0]['id']}})
        self.assertEqual(response.status, '201 Created')

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title',
                      'description': 'complaint description',
                      'author': author}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can add complaint only in active lot status')

    def test_patch_tender_award_complaint(self):
        #response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            #self.tender_id, self.award_id, self.tender_token),
            #{'data': {'status': 'unsuccessful'}})
        #self.assertEqual(response.status, '200 OK')
        #self.assertEqual(response.content_type, 'application/json')
        #self.assertEqual(response.json['data']['status'], 'unsuccessful')

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']
        owner_token = response.json['access']['token']

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, complaint['id'], owner_token), {'data': {'status': 'pending'}})

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']
        owner_token = response.json['access']['token']

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': {'reason': 'cancellation reason', 'status': 'active',
                                                'cancellationOf': 'lot', 'relatedLot': self.lots[0]['id']}})
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, complaint['id'], owner_token),
            {'data': {'status': 'pending'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can update complaint only in active lot status')


class TenderStage2EUAwardComplaintDocumentResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_tender_bids

    def setUp(self):
        super(TenderStage2EUAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author],
                                                'status': 'pending',
                                                'bid_id': self.bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, self.award_id), {'data': {'status': 'active', "qualified": True, "eligible": True}})
        # Create complaint for award
        response = self.app.post_json('/tenders/{}/awards/{}/complaints'.format(self.tender_id, self.award_id),
                                      {'data': {'title': 'complaint title',
                                                'description': 'complaint description',
                                                'author': author}})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']

    def test_not_found(self):
        response = self.app.post('/tenders/some_id/awards/some_id/complaints/some_id/documents',
                                 status=404,
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.post('/tenders/{}/awards/some_id/complaints/some_id/documents'.format(self.tender_id),
                                 status=404,
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        response = self.app.post('/tenders/{}/awards/{}/complaints/some_id/documents'.format(
            self.tender_id, self.award_id), status=404, upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'complaint_id'}
        ])

        response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents'.format(
            self.tender_id, self.award_id, self.complaint_id),
            status=404,
            upload_files=[('invalid_value', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.get('/tenders/some_id/awards/some_id/complaints/some_id/documents', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/awards/some_id/complaints/some_id/documents'.format(self.tender_id),
                                status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        response = self.app.get('/tenders/{}/awards/{}/complaints/some_id/documents'.format(self.tender_id,
                                                                                            self.award_id),
                                status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'complaint_id'}
        ])

        response = self.app.get('/tenders/some_id/awards/some_id/complaints/some_id/documents/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/awards/some_id/complaints/some_id/documents/some_id'.format(self.tender_id),
                                status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        response = self.app.get('/tenders/{}/awards/{}/complaints/some_id/documents/some_id'.format(self.tender_id,
                                                                                                    self.award_id),
                                status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'complaint_id'}
        ])

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents/some_id'.format(
            self.tender_id, self.award_id, self.complaint_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'document_id'}
        ])

        response = self.app.put('/tenders/some_id/awards/some_id/complaints/some_id/documents/some_id', status=404,
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.put('/tenders/{}/awards/some_id/complaints/some_id/documents/some_id'.format(self.tender_id),
                                status=404,
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        response = self.app.put('/tenders/{}/awards/{}/complaints/some_id/documents/some_id'.format(
            self.tender_id, self.award_id), status=404, upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'complaint_id'}
        ])

        response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/some_id'.format(
            self.tender_id, self.award_id, self.complaint_id),
            status=404,
            upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
        ])

    def test_create_tender_award_complaint_document(self):
        response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents'.format(
            self.tender_id, self.award_id, self.complaint_id),
            upload_files=[('file', 'name.doc', 'content')],
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't add document in current (draft) complaint status")

        response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token),
            upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json['data']['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name.doc', response.json['data']['title'])
        key = response.json['data']['url'].split('?')[-1]

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents'.format(
            self.tender_id, self.award_id, self.complaint_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data'][0]['id'])
        self.assertEqual('name.doc', response.json['data'][0]['title'])

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents?all=true'.format(
            self.tender_id, self.award_id, self.complaint_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data'][0]['id'])
        self.assertEqual('name.doc', response.json['data'][0]['title'])

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
        self.assertEqual(doc_id, response.json['data']['id'])
        self.assertEqual('name.doc', response.json['data']['title'])

        self.set_status('complete')

        response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents'.format(
            self.tender_id, self.award_id, self.complaint_id),
            upload_files=[('file', 'name.doc', 'content')],
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't add document in current (complete) tender status")

    def test_put_tender_award_complaint_document(self):
        response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token),
            upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json['data']['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id),
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
            self.tender_id, self.award_id, self.complaint_id, doc_id),
            upload_files=[('file', 'name.doc', 'content2')],
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can update document only author')

        response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token),
            upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        key = response.json['data']['url'].split('?')[-1]

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
        self.assertEqual(doc_id, response.json['data']['id'])
        self.assertEqual('name.doc', response.json['data']['title'])

        response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token),
            'content3',
            content_type='application/msword')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        key = response.json['data']['url'].split('?')[-1]

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents/{}?{}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content3')

        self.set_status('complete')

        response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token),
            upload_files=[('file', 'name.doc', 'content3')],
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't update document in current (complete) tender status")

    def test_patch_tender_award_complaint_document(self):
        response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token),
            upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json['data']['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}/documents/{}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id),
            {'data': {'description': 'document description'}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can update document only author')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token),
            {'data': {'description': 'document description'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents/{}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        self.assertEqual('document description', response.json['data']['description'])

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token),
            {'data': {'status': 'pending'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'pending')

        response = self.app.put(
            '/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(self.tender_id, self.award_id,
                                                                                   self.complaint_id, doc_id,
                                                                                   self.complaint_owner_token),
            'content2', content_type='application/msword')
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

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token),
            {'data': {'description': 'document description'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't update document in current (complete) tender status")


class TenderStage2EU2LotAwardComplaintDocumentResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_tender_bids
    initial_lots = deepcopy(2 * test_lots)

    def setUp(self):
        super(TenderStage2EU2LotAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        bid = self.bids[0]
        self.app.authorization = ('Basic', ('token', ''))
        self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                           {'data': {'suppliers': [author], 'status': 'pending', 'bid_id': bid['id'], 'lotID': bid['lotValues'][1]['relatedLot']}})
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author], 'status': 'pending',
                                                'bid_id': bid['id'], 'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, self.award_id), {'data': {'status': 'active', "qualified": True, "eligible": True}})
        # Create complaint for award
        response = self.app.post_json('/tenders/{}/awards/{}/complaints'.format(self.tender_id, self.award_id),
                                      {'data': {'title': 'complaint title',
                                                'description': 'complaint description',
                                                'author': author}})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']

    def test_create_tender_award_complaint_document(self):
        response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents'.format(
            self.tender_id, self.award_id, self.complaint_id),
            upload_files=[('file', 'name.doc', 'content')],
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't add document in current (draft) complaint status")

        response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token),
            upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json['data']['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name.doc', response.json['data']['title'])
        key = response.json['data']['url'].split('?')[-1]

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents'.format(
            self.tender_id, self.award_id, self.complaint_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data'][0]['id'])
        self.assertEqual('name.doc', response.json['data'][0]['title'])

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents?all=true'.format(
            self.tender_id, self.award_id, self.complaint_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data'][0]['id'])
        self.assertEqual('name.doc', response.json['data'][0]['title'])

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents/{}?download=some_id'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id),
            status=404)
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
        self.assertEqual(doc_id, response.json['data']['id'])
        self.assertEqual('name.doc', response.json['data']['title'])

        response = self.app.post_json('/tenders/{}/cancellations'.format(self.tender_id),
                                      {'data': {'reason': 'cancellation reason', 'status': 'active',
                                                'cancellationOf': 'lot', 'relatedLot': self.lots[0]['id']}})
        self.assertEqual(response.status, '201 Created')

        response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents'.format(
            self.tender_id, self.award_id, self.complaint_id),
            upload_files=[('file', 'name.doc', 'content')],
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         'Can add document only in active lot status')

    def test_put_tender_award_complaint_document(self):
        response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token),
            upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json['data']['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id),
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
            self.tender_id, self.award_id, self.complaint_id, doc_id),
            upload_files=[('file', 'name.doc', 'content2')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can update document only author')

        response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token),
            upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        key = response.json['data']['url'].split('?')[-1]

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
        self.assertEqual(doc_id, response.json['data']['id'])
        self.assertEqual('name.doc', response.json['data']['title'])

        response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token),
            'content3',
            content_type='application/msword')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        key = response.json['data']['url'].split('?')[-1]

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents/{}?{}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content3')

        #response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            #self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token),
            #{'data': {'status': 'pending'}})
        #self.assertEqual(response.status, '200 OK')
        #self.assertEqual(response.json['data']['status'], 'pending')

        response = self.app.put(
            '/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(self.tender_id, self.award_id,
                                                                                   self.complaint_id, doc_id,
                                                                                   self.complaint_owner_token),
            'content4', content_type='application/msword')
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
            "relatedLot": self.lots[0]['id']
        }})
        self.assertEqual(response.status, '201 Created')

        response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token),
            upload_files=[('file', 'name.doc', 'content3')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can update document only in active lot status")

    def test_patch_tender_award_complaint_document(self):
        response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token),
            upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json['data']['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}/documents/{}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id),
            {'data': {'description': 'document description'}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can update document only author')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token),
            {'data': {'description': 'document description'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents/{}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        self.assertEqual('document description', response.json['data']['description'])

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token),
            {'data': {'status': 'pending'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'pending')

        response = self.app.patch_json(
            '/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(self.tender_id, self.award_id,
                                                                                   self.complaint_id, doc_id,
                                                                                   self.complaint_owner_token),
            {"data": {"description": "document description2"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["description"], "document description2")

        response = self.app.post_json('/tenders/{}/cancellations'.format(self.tender_id),
                                      {'data': {'reason': 'cancellation reason', 'status': 'active',
                                                'cancellationOf': 'lot', 'relatedLot': self.lots[0]['id']}})
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token),
            {'data': {'description': 'document description'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         'Can update document only in active lot status')


class TenderStage2EUAwardDocumentResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_tender_bids

    def setUp(self):
        super(TenderStage2EUAwardDocumentResourceTest, self).setUp()
        # Create award
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author],
                                                'status': 'pending',
                                                'bid_id': self.bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']

    def test_not_found(self):
        response = self.app.post('/tenders/some_id/awards/some_id/documents',
                                 status=404,
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.post('/tenders/{}/awards/some_id/documents'.format(self.tender_id),
                                 status=404,
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        response = self.app.post('/tenders/{}/awards/{}/documents'.format(self.tender_id, self.award_id),
                                 status=404,
                                 upload_files=[('invalid_value', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.get('/tenders/some_id/awards/some_id/documents', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/awards/some_id/documents'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        response = self.app.get('/tenders/some_id/awards/some_id/documents/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/awards/some_id/documents/some_id'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        response = self.app.get('/tenders/{}/awards/{}/documents/some_id'.format(self.tender_id, self.award_id),
                                status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'document_id'}
        ])

        response = self.app.put('/tenders/some_id/awards/some_id/documents/some_id', status=404,
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.put('/tenders/{}/awards/some_id/documents/some_id'.format(self.tender_id),
                                status=404,
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        response = self.app.put('/tenders/{}/awards/{}/documents/some_id'.format(self.tender_id, self.award_id),
                                status=404,
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
        ])

    def test_create_tender_award_document(self):
        response = self.app.post('/tenders/{}/awards/{}/documents'.format(self.tender_id, self.award_id),
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json['data']['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name.doc', response.json['data']['title'])
        key = response.json['data']['url'].split('?')[-1]

        response = self.app.get('/tenders/{}/awards/{}/documents'.format(self.tender_id, self.award_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data'][0]['id'])
        self.assertEqual('name.doc', response.json['data'][0]['title'])

        response = self.app.get('/tenders/{}/awards/{}/documents?all=true'.format(self.tender_id, self.award_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data'][0]['id'])
        self.assertEqual('name.doc', response.json['data'][0]['title'])

        response = self.app.get('/tenders/{}/awards/{}/documents/{}?download=some_id'.format(self.tender_id,
                                                                                             self.award_id,
                                                                                             doc_id),
                                status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
        ])

        response = self.app.get('/tenders/{}/awards/{}/documents/{}?{}'.format(
            self.tender_id, self.award_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 7)
        self.assertEqual(response.body, 'content')

        response = self.app.get('/tenders/{}/awards/{}/documents/{}'.format(
            self.tender_id, self.award_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        self.assertEqual('name.doc', response.json['data']['title'])

        self.set_status('complete')

        response = self.app.post('/tenders/{}/awards/{}/documents'.format(self.tender_id, self.award_id),
                                 upload_files=[('file', 'name.doc', 'content')],
                                 status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't add document in current (complete) tender status")

    def test_put_tender_award_document(self):
        response = self.app.post('/tenders/{}/awards/{}/documents'.format(self.tender_id, self.award_id),
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json['data']['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.put('/tenders/{}/awards/{}/documents/{}'.format(self.tender_id, self.award_id, doc_id),
                                status=404,
                                upload_files=[('invalid_name', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.put('/tenders/{}/awards/{}/documents/{}'.format(self.tender_id, self.award_id, doc_id),
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        key = response.json['data']['url'].split('?')[-1]

        response = self.app.get('/tenders/{}/awards/{}/documents/{}?{}'.format(
            self.tender_id, self.award_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content2')

        response = self.app.get('/tenders/{}/awards/{}/documents/{}'.format(
            self.tender_id, self.award_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        self.assertEqual('name.doc', response.json['data']['title'])

        response = self.app.put('/tenders/{}/awards/{}/documents/{}'.format(
            self.tender_id, self.award_id, doc_id),
            'content3',
            content_type='application/msword')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        key = response.json['data']['url'].split('?')[-1]

        response = self.app.get('/tenders/{}/awards/{}/documents/{}?{}'.format(
            self.tender_id, self.award_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content3')

        self.set_status('complete')

        response = self.app.put('/tenders/{}/awards/{}/documents/{}'.format(self.tender_id, self.award_id, doc_id),
            upload_files=[('file', 'name.doc', 'content3')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't update document in current (complete) tender status")

    def test_patch_tender_award_document(self):
        response = self.app.post('/tenders/{}/awards/{}/documents'.format(self.tender_id, self.award_id),
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json['data']['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.patch_json('/tenders/{}/awards/{}/documents/{}'.format(
            self.tender_id, self.award_id, doc_id),
            {'data': {'description': 'document description'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])

        response = self.app.get('/tenders/{}/awards/{}/documents/{}'.format(self.tender_id, self.award_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        self.assertEqual('document description', response.json['data']['description'])

        self.set_status('complete')

        response = self.app.patch_json('/tenders/{}/awards/{}/documents/{}'.format(
            self.tender_id, self.award_id, doc_id),
            {'data': {'description': 'document description'}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't update document in current (complete) tender status")

    def test_create_award_document_bot(self):
        old_authorization = self.app.authorization
        self.app.authorization = ('Basic', ('bot', 'bot'))
        response = self.app.post('/tenders/{}/awards/{}/documents'.format(self.tender_id, self.award_id),
                                 upload_files=[('file', 'edr_request.yaml', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('edr_request.yaml', response.json["data"]["title"])
        if self.docservice:
            self.assertIn('Signature=', response.json["data"]["url"])
            self.assertIn('KeyID=', response.json["data"]["url"])
            self.assertNotIn('Expires=', response.json["data"]["url"])
            key = response.json["data"]["url"].split('/')[-1].split('?')[0]
            tender = self.db.get(self.tender_id)
            self.assertIn(key, tender['awards'][-1]['documents'][-1]["url"])
            self.assertIn('Signature=', tender['awards'][-1]['documents'][-1]["url"])
            self.assertIn('KeyID=', tender['awards'][-1]['documents'][-1]["url"])
            self.assertNotIn('Expires=', tender['awards'][-1]['documents'][-1]["url"])

        self.app.authorization = old_authorization

    def test_patch_not_author(self):
        authorization = self.app.authorization
        self.app.authorization = ('Basic', ('bot', 'bot'))
        response = self.app.post('/tenders/{}/awards/{}/documents'.format(self.tender_id, self.award_id),
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])

        self.app.authorization = authorization
        response = self.app.patch_json('/tenders/{}/awards/{}/documents/{}?acc_token={}'.format(self.tender_id, self.award_id, doc_id, self.tender_token),
                                       {"data": {"description": "document description"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can update document only author")
        self.app.authorization = authorization


class TenderStage2EU2LotAwardDocumentResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_tender_bids
    initial_lots = deepcopy(2 * test_lots)

    def setUp(self):
        super(TenderStage2EU2LotAwardDocumentResourceTest, self).setUp()
        # Create award
        bid = self.bids[0]
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author], 'status': 'pending',
                                                'bid_id': bid['id'], 'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']

    def test_create_tender_award_document(self):
        response = self.app.post('/tenders/{}/awards/{}/documents'.format(self.tender_id, self.award_id),
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json['data']['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name.doc', response.json['data']['title'])
        key = response.json['data']['url'].split('?')[-1]

        response = self.app.get('/tenders/{}/awards/{}/documents'.format(self.tender_id, self.award_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data'][0]['id'])
        self.assertEqual('name.doc', response.json['data'][0]['title'])

        response = self.app.get('/tenders/{}/awards/{}/documents?all=true'.format(self.tender_id, self.award_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data'][0]['id'])
        self.assertEqual('name.doc', response.json['data'][0]['title'])

        response = self.app.get('/tenders/{}/awards/{}/documents/{}?download=some_id'.format(
            self.tender_id, self.award_id, doc_id),
            status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
        ])

        response = self.app.get('/tenders/{}/awards/{}/documents/{}?{}'.format(
            self.tender_id, self.award_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 7)
        self.assertEqual(response.body, 'content')

        response = self.app.get('/tenders/{}/awards/{}/documents/{}'.format(
            self.tender_id, self.award_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        self.assertEqual('name.doc', response.json['data']['title'])

        response = self.app.post_json('/tenders/{}/cancellations'.format(self.tender_id),
                                      {'data': {'reason': 'cancellation reason', 'status': 'active',
                                                'cancellationOf': 'lot', 'relatedLot': self.lots[0]['id']}})
        self.assertEqual(response.status, '201 Created')

        response = self.app.post('/tenders/{}/awards/{}/documents'.format(self.tender_id, self.award_id),
                                 upload_files=[('file', 'name.doc', 'content')],
                                 status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         'Can add document only in active lot status')

    def test_put_tender_award_document(self):
        response = self.app.post('/tenders/{}/awards/{}/documents'.format(self.tender_id, self.award_id),
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json['data']['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.put('/tenders/{}/awards/{}/documents/{}'.format(self.tender_id, self.award_id, doc_id),
                                status=404,
                                upload_files=[('invalid_name', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.put('/tenders/{}/awards/{}/documents/{}'.format(self.tender_id, self.award_id, doc_id),
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        key = response.json['data']['url'].split('?')[-1]

        response = self.app.get('/tenders/{}/awards/{}/documents/{}?{}'.format(
            self.tender_id, self.award_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content2')

        response = self.app.get('/tenders/{}/awards/{}/documents/{}'.format(
            self.tender_id, self.award_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        self.assertEqual('name.doc', response.json['data']['title'])

        response = self.app.put('/tenders/{}/awards/{}/documents/{}'.format(
            self.tender_id, self.award_id, doc_id),
            'content3',
            content_type='application/msword')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        key = response.json['data']['url'].split('?')[-1]

        response = self.app.get('/tenders/{}/awards/{}/documents/{}?{}'.format(
            self.tender_id, self.award_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content3')

        response = self.app.post_json('/tenders/{}/cancellations'.format(self.tender_id),
                                      {'data': {'reason': 'cancellation reason', 'status': 'active',
                                                'cancellationOf': 'lot', 'relatedLot': self.lots[0]['id']}})
        self.assertEqual(response.status, '201 Created')

        response = self.app.put('/tenders/{}/awards/{}/documents/{}'.format(
            self.tender_id, self.award_id, doc_id),
            upload_files=[('file', 'name.doc', 'content3')],
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         'Can update document only in active lot status')

    def test_patch_tender_award_document(self):
        response = self.app.post('/tenders/{}/awards/{}/documents'.format(self.tender_id, self.award_id),
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json['data']['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.patch_json('/tenders/{}/awards/{}/documents/{}'.format(
            self.tender_id, self.award_id, doc_id),
            {'data': {'description': 'document description'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])

        response = self.app.get('/tenders/{}/awards/{}/documents/{}'.format(self.tender_id, self.award_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        self.assertEqual('document description', response.json['data']['description'])

        response = self.app.post_json('/tenders/{}/cancellations'.format(self.tender_id),
                                      {'data': {'reason': 'cancellation reason', 'status': 'active',
                                                'cancellationOf': 'lot', 'relatedLot': self.lots[0]['id']}})
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json('/tenders/{}/awards/{}/documents/{}'.format(
            self.tender_id, self.award_id, doc_id),
            {'data': {'description': 'document description'}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can update document only in active lot status')


class TenderStage2UAAwardResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_tender_bids

    def test_create_tender_award_invalid(self):
        self.app.authorization = ('Basic', ('token', ''))
        request_path = '/tenders/{}/awards'.format(self.tender_id)
        response = self.app.post(request_path, 'data', status=415)
        self.assertEqual(response.status, '415 Unsupported Media Type')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description':
                u"Content-Type header should be one of ['application/json']",
             u'location': u'header', u'name': u'Content-Type'}
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
                u'Please use a mapping for this field or Identifier instance instead of unicode.']},
                u'location': u'body', u'name': u'suppliers'}
        ])

        response = self.app.post_json(request_path, {
                                      'data': {'suppliers': [{'identifier': {'id': 0}}]}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'contactPoint': [u'This field is required.'],
                               u'identifier': {u'scheme': [u'This field is required.']},
                               u'name': [u'This field is required.'],
                               u'address': [u'This field is required.']}],
             u'location': u'body', u'name': u'suppliers'},
            {u'description': [u'This field is required.'],
             u'location': u'body', u'name': u'bid_id'}
        ])

        response = self.app.post_json(request_path, {'data': {'suppliers': [
                                      {'name': 'name', 'identifier': {'uri': 'invalid_value'}}]}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'contactPoint': [u'This field is required.'],
                               u'identifier': {u'scheme': [u'This field is required.'],
                                               u'id': [u'This field is required.'],
                                               u'uri': [u'Not a well formed URL.']},
                               u'address': [u'This field is required.']}],
             u'location': u'body', u'name': u'suppliers'},
            {u'description': [u'This field is required.'],
             u'location': u'body', u'name': u'bid_id'}
        ])

        response = self.app.post_json(request_path,
                                      {'data': {'suppliers': [author],
                                                'status': 'pending',
                                                'bid_id': self.bids[0]['id'],
                                                'lotID': '0' * 32}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'lotID should be one of lots'], u'location': u'body', u'name': u'lotID'}
        ])

        response = self.app.post_json('/tenders/some_id/awards',
                                      {'data': {'suppliers': [author], 'bid_id': self.bids[0]['id']}},
                                      status=404)
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

        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author],
                                                'status': 'pending',
                                                'bid_id': self.bids[0]['id']}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't create award in current (complete) tender status")

    def test_create_tender_award(self):
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))

        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author],
                                                'status': 'pending',
                                                'bid_id': self.bids[0]['id']}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        award = response.json['data']
        self.assertEqual(award['suppliers'][0]['name'], author['name'])
        self.assertIn('id', award)
        self.assertIn(award['id'], response.headers['Location'])

        self.app.authorization = auth

        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'][-1], award)

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, award['id'], self.tender_token),
            {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'active')

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'active.awarded')

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, award['id'], self.tender_token), {'data': {'status': 'cancelled'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'cancelled')
        self.assertIn('Location', response.headers)

    def test_patch_tender_award(self):
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author], 'status': u'pending',
                                                'bid_id': self.bids[0]['id'], 'value': {'amount': 500}}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        award = response.json['data']

        self.app.authorization = auth
        response = self.app.patch_json('/tenders/{}/awards/some_id'.format(self.tender_id),
                                       {'data': {'status': 'unsuccessful'}},
                                       status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        response = self.app.patch_json('/tenders/some_id/awards/some_id',
                                       {'data': {'status': 'unsuccessful'}},
                                       status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, award['id'], self.tender_token),
            {'data': {'awardStatus': 'unsuccessful'}},
            status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'], [{'location': 'body',
                                                    'name': 'awardStatus',
                                                    'description': 'Rogue field'}])

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, award['id'], self.tender_token),
            {'data': {'status': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)
        new_award_location = response.headers['Location']

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, award['id'], self.tender_token), {'data': {'status': 'pending'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't update award in current (unsuccessful) status")

        request_path = '/tenders/{}/awards'.format(self.tender_id)
        response = self.app.get(request_path)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 2)
        self.assertIn(response.json['data'][1]['id'], new_award_location)
        new_award = response.json['data'][-1]
        old_date = new_award['date']

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, new_award['id'], self.tender_token),
            {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertNotEqual(old_date, response.json['data']['date'])
        old_date = response.json['data']['date']

        response = self.app.get(request_path)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 2)

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, new_award['id'], self.tender_token), {'data': {'status': 'cancelled'}})
        self.assertNotEqual(old_date, response.json['data']['date'])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)

        response = self.app.get(request_path)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 3)

        self.set_status('complete')

        response = self.app.get('/tenders/{}/awards/{}'.format(self.tender_id, award['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['value']['amount'], 500)

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, award['id'], self.tender_token), {'data': {'status': 'unsuccessful'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't update award in current (complete) tender status")

    def test_patch_tender_award_active(self):
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json( '/tenders/{}/awards'.format(self.tender_id),
                                       {'data': {'suppliers': [author], 'status': u'pending',
                                                 'bid_id': self.bids[0]['id'], 'value': {'amount': 500}}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        award = response.json['data']

        self.app.authorization = auth
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, award['id'], self.tender_token), {'data': {'status': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)
        new_award_location = response.headers['Location']

        response = self.app.patch_json(new_award_location[-81:]+'?acc_token={}'.format(self.tender_token),
                                       {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertNotIn('Location', response.headers)

        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 2)

        bid_token = self.initial_bids_tokens[self.bids[0]['id']]
        response = self.app.post_json(new_award_location[-81:]+'/complaints?acc_token={}'.format(bid_token),
                                      {'data': {'title': 'complaint title', 'description': 'complaint description',
                                                'author': author, 'status': 'pending'}})
        self.assertEqual(response.status, '201 Created')

        self.app.authorization = ('Basic', ('reviewer', ''))
        response = self.app.patch_json(new_award_location[-81:]+'/complaints/{}'.format(response.json['data']['id']),
                                       {'data': {'status': 'accepted'}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(new_award_location[-81:]+'/complaints/{}'.format(response.json['data']['id']),
                                       {'data': {'status': 'satisfied'}})
        self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.patch_json(new_award_location[-81:], {'data': {'status': 'cancelled'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)
        new_award_location = response.headers['Location']

        response = self.app.patch_json(new_award_location[-81:], {'data': {'status': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)
        new_award_location = response.headers['Location']

        response = self.app.patch_json(new_award_location[-81:], {'data': {'status': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertNotIn('Location', response.headers)

        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 4)

    def test_patch_tender_award_unsuccessful(self):
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author], 'status': u'pending',
                                                'bid_id': self.bids[0]['id'], 'value': {'amount': 500}}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        award = response.json['data']

        self.app.authorization = auth
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, award['id'], self.tender_token), {'data': {'status': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)
        new_award_location = response.headers['Location']

        response = self.app.patch_json(new_award_location[-81:]+'?acc_token={}'.format(self.tender_token),
                                       {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertNotIn('Location', response.headers)

        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 2)

        bid_token = self.initial_bids_tokens[self.bids[0]['id']]
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, award['id'], bid_token),
            {'data': {'title': 'complaint title',
                      'description': 'complaint description',
                      'author': author,
                      'status': 'pending'}})
        self.assertEqual(response.status, '201 Created')

        self.app.authorization = ('Basic', ('reviewer', ''))
        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(
            self.tender_id, award['id'], response.json['data']['id']),
            {'data': {'status': 'accepted'}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(
            self.tender_id, award['id'], response.json['data']['id']),
            {'data': {'status': 'satisfied'}})
        self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('{}/complaints'.format(new_award_location[-81:]),
                                      {'data': {'title': 'complaint title',
                                                'description': 'complaint description',
                                                'author': author}})
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, award['id']),
                                       {'data': {'status': 'cancelled'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)
        new_award_location = response.headers['Location']

        response = self.app.patch_json(new_award_location[-81:], {'data': {'status': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)
        new_award_location = response.headers['Location']

        response = self.app.patch_json(new_award_location[-81:], {'data': {'status': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertNotIn('Location', response.headers)

        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 4)

    def test_get_tender_award(self):
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author],
                                                'status': 'pending',
                                                'bid_id': self.bids[0]['id']}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        award = response.json['data']

        self.app.auth = auth
        response = self.app.get('/tenders/{}/awards/{}'.format(self.tender_id, award['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        award_data = response.json['data']
        self.assertEqual(award_data, award)

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

    def test_patch_tender_award_Administrator_change(self):
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author],
                                                'status': 'pending',
                                                'bid_id': self.bids[0]['id']}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        award = response.json['data']
        complaintPeriod = award['complaintPeriod'][u'startDate']

        self.app.authorization = ('Basic', ('administrator', ''))
        response = self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, award['id']),
                                       {'data': {'complaintPeriod': {'endDate': award['complaintPeriod'][u'startDate']}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('endDate', response.json['data']['complaintPeriod'])
        self.assertEqual(response.json['data']['complaintPeriod']['endDate'], complaintPeriod)


class TenderStage2UALotAwardResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = 'active.qualification'
    initial_lots = deepcopy(test_lots)
    initial_bids = test_tender_bids

    def test_create_tender_award(self):
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author],
                                                'status': 'pending',
                                                'bid_id': self.bids[0]['id']}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'],
                         [{'location': 'body', 'name': 'lotID', 'description': ['This field is required.']}])

        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author],
                                                'status': 'pending',
                                                'bid_id': self.bids[0]['id'],
                                                'lotID': self.lots[0]['id']}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        award = response.json['data']
        self.assertEqual(award['suppliers'][0]['name'], author['name'])
        self.assertEqual(award['lotID'], self.lots[0]['id'])
        self.assertIn('id', award)
        self.assertIn(award['id'], response.headers['Location'])

        self.app.authorization = auth
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'][-1], award)

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, award['id'], self.tender_token),
            {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'active')

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'active.awarded')

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, award['id'], self.tender_token),
            {'data': {'status': 'cancelled'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'cancelled')
        self.assertIn('Location', response.headers)

    def test_patch_tender_award(self):
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author], 'status': u'pending',
                                                'bid_id': self.bids[0]['id'], 'lotID': self.lots[0]['id'],
                                                'value': {'amount': 500}}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        award = response.json['data']

        self.app.authorization = auth
        response = self.app.patch_json('/tenders/{}/awards/some_id?acc_token={}'.format(
            self.tender_id, self.tender_token),
            {'data': {'status': 'unsuccessful'}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        response = self.app.patch_json('/tenders/some_id/awards/some_id',
                                       {'data': {'status': 'unsuccessful'}},
                                       status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, award['id'], self.tender_token),
            {'data': {'awardStatus': 'unsuccessful'}},
            status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'],
                         [{'location': 'body',
                           'name': 'awardStatus',
                           'description': 'Rogue field'}])

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, award['id'], self.tender_token),
            {'data': {'title': 'title', 'description': 'description', 'status': 'unsuccessful'}})

        self.assertEqual(response.json['data']['title'], 'title')
        self.assertEqual(response.json['data']['description'], 'description')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)
        new_award_location = response.headers['Location']

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, award['id'], self.tender_token), {'data': {'status': 'pending'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't update award in current (unsuccessful) status")

        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 2)
        self.assertIn(response.json['data'][-1]['id'], new_award_location)
        new_award = response.json['data'][-1]

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, new_award['id'], self.tender_token),
            {'data': {'status': 'active', 'eligible': True}},
            status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'],
                         [{'location': 'body', 'name': 'qualified', 'description': ['This field is required.']}])
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, new_award['id'], self.tender_token),
            {'data': {'title': 'title', 'description': 'description', 'qualified': True, 'eligible': True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['qualified'], True)
        self.assertEqual(response.json['data']['eligible'], True)
        self.assertEqual(response.json['data']['title'], 'title')
        self.assertEqual(response.json['data']['description'], 'description')

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, new_award['id'], self.tender_token),
            {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 2)

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, new_award['id'], self.tender_token), {'data': {'status': 'cancelled'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)

        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 3)

        self.set_status('complete')

        response = self.app.get('/tenders/{}/awards/{}'.format(self.tender_id, award['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['value']['amount'], 500)

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, award['id'], self.tender_token), {'data': {'status': 'unsuccessful'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't update award in current (complete) tender status")

    def test_patch_tender_award_unsuccessful(self):
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))

        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author], 'status': u'pending',
                                                'bid_id': self.bids[0]['id'], 'lotID': self.lots[0]['id'],
                                                'value': {'amount': 500}}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        award = response.json['data']

        self.app.authorization = auth
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, award['id'], self.tender_token), {'data': {'status': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)
        new_award_location = response.headers['Location']

        response = self.app.patch_json(new_award_location[-81:]+'?acc_token={}'.format(self.tender_token),
                                       {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertNotIn('Location', response.headers)

        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 2)

        bid_token = self.initial_bids_tokens[self.bids[0]['id']]
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, award['id'], bid_token),
            {'data': {'title': 'complaint title',
                      'description': 'complaint description',
                      'author': author,
                      'status': 'pending'}})
        self.assertEqual(response.status, '201 Created')

        self.app.authorization = ('Basic', ('reviewer', ''))
        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(
            self.tender_id, award['id'], response.json['data']['id']),
            {'data': {'status': 'accepted'}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(
            self.tender_id, award['id'], response.json['data']['id']), {'data': {'status': 'satisfied'}})
        self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('{}/complaints'.format(new_award_location[-81:]),
                                      {'data': {'title': 'complaint title',
                                                'description': 'complaint description',
                                                'author': author}})
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, award['id']),
                                       {'data': {'status': 'cancelled'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)
        new_award_location = response.headers['Location']

        response = self.app.patch_json(new_award_location[-81:], {'data': {'status': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('Location', response.headers)
        new_award_location = response.headers['Location']

        response = self.app.patch_json(new_award_location[-81:], {'data': {'status': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertNotIn('Location', response.headers)

        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 4)


class TenderStage2UA2LotAwardResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = 'active.qualification'
    initial_lots = deepcopy(2 * test_lots)
    initial_bids = test_tender_bids

    def test_create_tender_award(self):
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': {'reason': 'cancellation reason', 'status': 'active',
                                                'cancellationOf': 'lot', 'relatedLot': self.lots[0]['id']}})
        self.assertEqual(response.status, '201 Created')

        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author], 'status': 'pending',
                                                'bid_id': self.bids[0]['id'], 'lotID': self.lots[0]['id']}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can create award only in active lot status')

        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author], 'status': 'pending',
                                                'bid_id': self.bids[0]['id'], 'lotID': self.lots[1]['id']}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        award = response.json['data']
        self.assertEqual(award['suppliers'][0]['name'], author['name'])
        self.assertEqual(award['lotID'], self.lots[1]['id'])
        self.assertIn('id', award)
        self.assertIn(award['id'], response.headers['Location'])

        self.app.authorization = auth
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'][-1], award)

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, award['id'], self.tender_token),
            {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'active')

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'active.awarded')

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, award['id'], self.tender_token), {'data': {'status': 'cancelled'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'cancelled')
        self.assertIn('Location', response.headers)

    def test_patch_tender_award(self):

        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))

        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author], 'status': u'pending',
                                                'bid_id': self.bids[0]['id'], 'lotID': self.lots[0]['id'],
                                                'value': {'amount': 500}}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        award = response.json['data']

        self.app.authorization = auth
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, award['id'], self.tender_token),
            {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 2)
        new_award = response.json['data'][-1]

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason', 'status': 'active',
                                                'cancellationOf': 'lot', 'relatedLot': self.lots[1]['id']}})
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, new_award['id'], self.tender_token), {'data': {'status': 'unsuccessful'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can update award only in active lot status')


class TenderStage2UAAwardComplaintResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_tender_bids

    def setUp(self):
        super(TenderStage2UAAwardComplaintResourceTest, self).setUp()
        # Create award
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author],
                                                'status': 'pending',
                                                'bid_id': self.bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, self.award_id), {'data': {'status': 'active', "qualified": True, "eligible": True}})
        self.app.authorization = auth
        self.bid_token = self.initial_bids_tokens[self.bids[0]['id']]

    def test_create_tender_award_complaint_invalid(self):
        response = self.app.post_json('/tenders/some_id/awards/some_id/complaints',
                                      {'data': {'title': 'complaint title',
                                                'description': 'complaint description',
                                                'author': author}},
                                      status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}
        ])

        request_path = '/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token)

        response = self.app.post(request_path, 'data', status=415)
        self.assertEqual(response.status, '415 Unsupported Media Type')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description':
                u"Content-Type header should be one of ['application/json']",
             u'location': u'header',
             u'name': u'Content-Type'}
        ])

        response = self.app.post(request_path, 'data', content_type='application/json', status=422)
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

        response = self.app.post_json(request_path, {'data': {}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'author'},
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'title'},
        ])

        response = self.app.post_json(request_path, {'data': {'invalid_field': 'invalid_value'}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Rogue field', u'location':
                u'body', u'name': u'invalid_field'}
        ])

        response = self.app.post_json(request_path, {'data': {'author': {'identifier': 'invalid_value'}}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': {u'identifier': [
                u'Please use a mapping for this field or Identifier instance instead of unicode.']},
                u'location': u'body',
                u'name': u'author'}
        ])

        response = self.app.post_json(request_path,
                                      {'data': {'title': 'complaint title',
                                                'description': 'complaint description',
                                                'author': {'identifier': {'id': 0}}}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': {u'contactPoint': [u'This field is required.'],
                              u'identifier': {u'scheme': [u'This field is required.']},
                              u'name': [u'This field is required.'],
                              u'address': [u'This field is required.']},
             u'location': u'body', u'name': u'author'}
        ])

        response = self.app.post_json(request_path,
                                      {'data': {'title': 'complaint title',
                                                'description': 'complaint description',
                                                'author': {'name': 'name', 'identifier': {'uri': 'invalid_value'}}}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': {u'contactPoint': [u'This field is required.'],
                              u'identifier': {u'scheme': [u'This field is required.'],
                                              u'id': [u'This field is required.'],
                                              u'uri': [u'Not a well formed URL.']},
                              u'address': [u'This field is required.']},
             u'location': u'body',
             u'name': u'author'}
        ])

    def test_create_tender_award_complaint(self):
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title', 'description': 'complaint description',
                      'author': author, 'status': 'pending'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']
        self.assertEqual(complaint['author']['name'], author['name'])
        self.assertIn('id', complaint)
        self.assertIn(complaint['id'], response.headers['Location'])

        self.set_status('active.awarded')

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'active.awarded')

        self.set_status('unsuccessful')

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title',
                      'description': 'complaint description',
                      'author': author}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't add complaint in current (unsuccessful) tender status")

    def test_patch_tender_award_complaint(self):
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']
        owner_token = response.json['access']['token']

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(
            self.tender_id, self.award_id, complaint['id']), {'data': {'status': 'cancelled',
                                                                       'cancellationReason': 'reason'}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Forbidden')

        #response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            #self.tender_id, self.award_id, self.tender_token),
            #{'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        #self.assertEqual(response.status, '200 OK')
        #self.assertEqual(response.content_type, 'application/json')
        #self.assertEqual(response.json['data']['status'], 'active')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, complaint['id'], owner_token),
            {'data': {'title': 'claim title',}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['title'], 'claim title')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, complaint['id'], owner_token), {'data': {'status': 'pending'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'pending')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, complaint['id'], owner_token),
            {'data': {'status': 'stopping', 'cancellationReason': 'reason'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'stopping')
        self.assertEqual(response.json['data']['cancellationReason'], 'reason')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/some_id'.format(self.tender_id, self.award_id),
                                       {'data': {'status': 'resolved', 'resolution': 'resolution text'}},
                                       status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'complaint_id'}
        ])

        response = self.app.patch_json('/tenders/some_id/awards/some_id/complaints/some_id',
                                       {'data': {'status': 'resolved', 'resolution': 'resolution text'}},
                                       status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, complaint['id'], owner_token),
            {'data': {'status': 'cancelled', 'cancellationReason': 'reason'}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], "Can't update complaint")

        response = self.app.patch_json('/tenders/{}/awards/some_id/complaints/some_id'.format(self.tender_id),
                                       {'data': {'status': 'resolved', 'resolution': 'resolution text'}},
                                       status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}'.format(
            self.tender_id, self.award_id, complaint['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'stopping')
        self.assertEqual(response.json['data']['cancellationReason'], 'reason')

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']
        owner_token = response.json['access']['token']

        self.set_status('complete')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, complaint['id'], owner_token),
            {'data': {'status': 'claim'}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't update complaint in current (complete) tender status")

    def test_review_tender_award_complaint(self):
        for status in ['invalid', 'declined', 'satisfied']:
            self.app.authorization = ('Basic', ('token', ''))
            response = self.app.post_json('/tenders/{}/awards/{}/complaints'.format(self.tender_id, self.award_id),
                                          {'data': {'title': 'complaint title', 'description': 'complaint description',
                                                    'author': author, 'status': 'pending'}})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            complaint = response.json['data']

            self.app.authorization = ('Basic', ('reviewer', ''))
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(
                self.tender_id, self.award_id, complaint['id']),
                {'data': {'decision': '{} complaint'.format(status)}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.json['data']['decision'], '{} complaint'.format(status))

            if status != 'invalid':
                response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(
                    self.tender_id, self.award_id, complaint['id']), {'data': {'status': 'accepted'}})
                self.assertEqual(response.status, '200 OK')
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.json['data']['status'], 'accepted')

                response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(
                    self.tender_id, self.award_id, complaint['id']),
                    {'data': {'decision': 'accepted:{} complaint'.format(status)}})
                self.assertEqual(response.status, '200 OK')
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.json['data']['decision'], 'accepted:{} complaint'.format(status))

            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(
                self.tender_id, self.award_id, complaint['id']),
                {'data': {'status': status}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.json['data']['status'], status)

    def test_get_tender_award_complaint(self):
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}'.format(
            self.tender_id, self.award_id, complaint['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], complaint)

        response = self.app.get('/tenders/{}/awards/{}/complaints/some_id'.format(self.tender_id, self.award_id),
                                status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'complaint_id'}
        ])

        response = self.app.get('/tenders/some_id/awards/some_id/complaints/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

    def test_get_tender_award_complaints(self):
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']

        response = self.app.get('/tenders/{}/awards/{}/complaints'.format(self.tender_id, self.award_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'][0], complaint)

        response = self.app.get('/tenders/some_id/awards/some_id/complaints', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': author}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can add complaint only in complaintPeriod')


class TenderStage2UALotAwardComplaintResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = 'active.qualification'
    initial_lots = deepcopy(test_lots)
    initial_bids = test_tender_bids

    def setUp(self):
        super(TenderStage2UALotAwardComplaintResourceTest, self).setUp()
        # Create award
        bid = self.bids[0]
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author], 'status': 'pending',
                                                'bid_id': bid['id'], 'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, self.award_id), {'data': {'status': 'active', "qualified": True, "eligible": True}})
        self.bid_token = self.initial_bids_tokens[self.bids[0]['id']]
        self.app.authorization = auth

    def test_create_tender_award_complaint(self):
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title', 'description': 'complaint description',
                      'author': author, 'status': 'pending'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']
        self.assertEqual(complaint['author']['name'], author['name'])
        self.assertIn('id', complaint)
        self.assertIn(complaint['id'], response.headers['Location'])

        self.set_status('active.awarded')

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'active.awarded')

        self.set_status('unsuccessful')

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': author}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't add complaint in current (unsuccessful) tender status")

    def test_patch_tender_award_complaint(self):
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']
        owner_token = response.json['access']['token']

        #response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            #self.tender_id, self.award_id, self.tender_token),
            #{'data': {'status': 'active', 'qualified': True, 'eligible': True}})
        #self.assertEqual(response.status, '200 OK')
        #self.assertEqual(response.content_type, 'application/json')
        #self.assertEqual(response.json['data']['status'], 'active')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, complaint['id'], owner_token), {'data': {'status': 'pending'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'pending')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, complaint['id'], owner_token),
            {'data': {'status': 'stopping', 'cancellationReason': 'reason'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'stopping')
        self.assertEqual(response.json['data']['cancellationReason'], 'reason')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/some_id?acc_token={}'.format(
            self.tender_id, self.award_id, owner_token),
            {'data': {'status': 'resolved', 'resolution': 'resolution text'}},
            status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'complaint_id'}
        ])

        response = self.app.patch_json('/tenders/some_id/awards/some_id/complaints/some_id',
                                       {'data': {'status': 'resolved', 'resolution': 'resolution text'}},
                                       status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, complaint['id'], owner_token),
            {'data': {'status': 'cancelled', 'cancellationReason': 'reason'}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], "Can't update complaint")

        response = self.app.patch_json('/tenders/{}/awards/some_id/complaints/some_id?acc_token={}'.format(
            self.tender_id, owner_token),
            {'data': {'status': 'resolved', 'resolution': 'resolution text'}},
            status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, self.award_id, complaint['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'stopping')
        self.assertEqual(response.json['data']['cancellationReason'], 'reason')

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']
        owner_token = response.json['access']['token']

        self.set_status('complete')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, complaint['id'], owner_token),
            {'data': {'status': 'claim'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't update complaint in current (complete) tender status")

    def test_get_tender_award_complaint(self):
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}'.format(
            self.tender_id, self.award_id, complaint['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], complaint)

        response = self.app.get('/tenders/{}/awards/{}/complaints/some_id'.format(self.tender_id, self.award_id),
                                status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'complaint_id'}
        ])

        response = self.app.get('/tenders/some_id/awards/some_id/complaints/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

    def test_get_tender_award_complaints(self):
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']

        response = self.app.get('/tenders/{}/awards/{}/complaints'.format(self.tender_id, self.award_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'][0], complaint)

        response = self.app.get('/tenders/some_id/awards/some_id/complaints', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.bid_token),
            {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': author}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can add complaint only in complaintPeriod')


class Tender2LotAwardComplaintResourceTest(TenderStage2UALotAwardComplaintResourceTest):
    initial_lots = deepcopy(2 * test_lots)

    def test_create_tender_award_complaint(self):
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.initial_bids_tokens[self.bids[0]['id']]),
            {'data': {'title': 'complaint title', 'description': 'complaint description',
                      'author': author, 'status': 'pending'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']
        self.assertEqual(complaint['author']['name'], author['name'])
        self.assertIn('id', complaint)
        self.assertIn(complaint['id'], response.headers['Location'])

        self.set_status('active.awarded')

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'active.awarded')

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': {'reason': 'cancellation reason', 'status': 'active',
                                                'cancellationOf': 'lot', 'relatedLot': self.lots[0]['id']}})
        self.assertEqual(response.status, '201 Created')

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.initial_bids_tokens[self.bids[0]['id']]),
            {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': author}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can add complaint only in active lot status')

    def test_patch_tender_award_complaint(self):
        #response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            #self.tender_id, self.award_id, self.tender_token), {'data': {'status': 'unsuccessful'}})
        #self.assertEqual(response.status, '200 OK')
        #self.assertEqual(response.content_type, 'application/json')
        #self.assertEqual(response.json['data']['status'], 'unsuccessful')

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.initial_bids_tokens[self.bids[0]['id']]),
            {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']
        owner_token = response.json['access']['token']

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, complaint['id'], owner_token),
            {'data': {'status': 'pending'}})

        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, self.initial_bids_tokens[self.bids[0]['id']]),
            {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': author}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']
        owner_token = response.json['access']['token']

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason', 'status': 'active',
                                                'cancellationOf': 'lot', 'relatedLot': self.lots[0]['id']}})
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, complaint['id'], owner_token), {'data': {'status': 'pending'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can update complaint only in active lot status')


class TenderStage2UAAwardComplaintDocumentResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_tender_bids

    def setUp(self):
        super(TenderStage2UAAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author],
                                                'status': 'pending',
                                                'bid_id': self.bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, self.award_id), {'data': {'status': 'active', "qualified": True, "eligible": True}})
        self.app.authorization = auth

        # Create complaint for award
        bid_token = self.initial_bids_tokens[self.bids[0]['id']]
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, bid_token),
            {'data': {'title': 'complaint title',
                      'description': 'complaint description',
                      'author': author}})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']

    def test_not_found(self):
        response = self.app.post('/tenders/some_id/awards/some_id/complaints/some_id/documents',
                                 status=404,
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.post('/tenders/{}/awards/some_id/complaints/some_id/documents'.format(self.tender_id),
                                 status=404,
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        response = self.app.post('/tenders/{}/awards/{}/complaints/some_id/documents'.format(
            self.tender_id, self.award_id),
            status=404,
            upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'complaint_id'}
        ])

        response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token),
            status=404,
            upload_files=[('invalid_value', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.get('/tenders/some_id/awards/some_id/complaints/some_id/documents', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/awards/some_id/complaints/some_id/documents'.format(self.tender_id),
                                status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        response = self.app.get('/tenders/{}/awards/{}/complaints/some_id/documents'.format(self.tender_id,
                                                                                            self.award_id),
                                status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'complaint_id'}
        ])

        response = self.app.get('/tenders/some_id/awards/some_id/complaints/some_id/documents/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/awards/some_id/complaints/some_id/documents/some_id'.format(self.tender_id),
                                status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        response = self.app.get('/tenders/{}/awards/{}/complaints/some_id/documents/some_id'.format(self.tender_id,
                                                                                                    self.award_id),
                                status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'complaint_id'}
        ])

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents/some_id'.format(
            self.tender_id, self.award_id, self.complaint_id),
            status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'document_id'}
        ])

        response = self.app.put('/tenders/some_id/awards/some_id/complaints/some_id/documents/some_id', status=404,
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.put('/tenders/{}/awards/some_id/complaints/some_id/documents/some_id'.format(self.tender_id),
                                status=404,
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        response = self.app.put('/tenders/{}/awards/{}/complaints/some_id/documents/some_id'.format(self.tender_id,
                                                                                                    self.award_id),
                                status=404,
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'complaint_id'}
        ])

        response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/some_id'.format(
            self.tender_id, self.award_id, self.complaint_id),
            status=404,
            upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
        ])

    def test_create_tender_award_complaint_document(self):
        response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, self.tender_token),
            upload_files=[('file', 'name.doc', 'content')],
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't add document in current (draft) complaint status")

        response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token),
            upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json['data']['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name.doc', response.json['data']['title'])
        key = response.json['data']['url'].split('?')[-1]

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents'.format(
            self.tender_id, self.award_id, self.complaint_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data'][0]['id'])
        self.assertEqual('name.doc', response.json['data'][0]['title'])

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents?all=true'.format(
            self.tender_id, self.award_id, self.complaint_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data'][0]['id'])
        self.assertEqual('name.doc', response.json['data'][0]['title'])

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents/{}?download=some_id'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id),
            status=404)
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
        self.assertEqual(doc_id, response.json['data']['id'])
        self.assertEqual('name.doc', response.json['data']['title'])

        self.set_status('complete')

        response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token),
            upload_files=[('file', 'name.doc', 'content')],
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't add document in current (complete) tender status")

    def test_put_tender_award_complaint_document(self):
        response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token),
            upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json['data']['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.tender_token),
            status=404,
            upload_files=[('invalid_name', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.tender_token),
            upload_files=[('file', 'name.doc', 'content2')],
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can update document only author')

        response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token),
            upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        key = response.json['data']['url'].split('?')[-1]

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
        self.assertEqual(doc_id, response.json['data']['id'])
        self.assertEqual('name.doc', response.json['data']['title'])

        response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token),
            'content3',
            content_type='application/msword')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        key = response.json['data']['url'].split('?')[-1]

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents/{}?{}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content3')

        self.set_status('complete')

        response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token),
            upload_files=[('file', 'name.doc', 'content3')],
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't update document in current (complete) tender status")

    def test_patch_tender_award_complaint_document(self):
        response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token),
            upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json['data']['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.tender_token),
            {'data': {'description': 'document description'}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can update document only author')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token),
            {'data': {'description': 'document description'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents/{}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        self.assertEqual('document description', response.json['data']['description'])

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token),
            {'data': {'status': 'pending'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'pending')

        response = self.app.put(
            '/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(self.tender_id, self.award_id,
                                                                                   self.complaint_id, doc_id,
                                                                                   self.complaint_owner_token),
            'content2', content_type='application/msword')
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

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token),
            {'data': {'description': 'document description'}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't update document in current (complete) tender status")


class TenderStage2UA2LotAwardComplaintDocumentResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_tender_bids
    initial_lots = deepcopy(2 * test_lots)

    def setUp(self):
        super(TenderStage2UA2LotAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        bid = self.bids[0]
        bid_token = self.initial_bids_tokens[self.bids[0]['id']]
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author], 'status': 'pending',
                                                'bid_id': bid['id'], 'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, self.award_id), {'data': {'status': 'active', "qualified": True, "eligible": True}})
        self.app.authorization = auth
        # Create complaint for award
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(
            self.tender_id, self.award_id, bid_token),
            {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': author}})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']

    def test_create_tender_award_complaint_document(self):
        response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, self.tender_token),
            upload_files=[('file', 'name.doc', 'content')],
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't add document in current (draft) complaint status")

        response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token),
            upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json['data']['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name.doc', response.json['data']['title'])
        key = response.json['data']['url'].split('?')[-1]

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents'.format(
            self.tender_id, self.award_id, self.complaint_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data'][0]['id'])
        self.assertEqual('name.doc', response.json['data'][0]['title'])

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents?all=true'.format(
            self.tender_id, self.award_id, self.complaint_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data'][0]['id'])
        self.assertEqual('name.doc', response.json['data'][0]['title'])

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents/{}?download=some_id'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id),
            status=404)
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
        self.assertEqual(doc_id, response.json['data']['id'])
        self.assertEqual('name.doc', response.json['data']['title'])

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason', 'status': 'active',
                                                'cancellationOf': 'lot', 'relatedLot': self.lots[0]['id']}})
        self.assertEqual(response.status, '201 Created')

        response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token),
            upload_files=[('file', 'name.doc', 'content')],
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         'Can add document only in active lot status')

    def test_put_tender_award_complaint_document(self):
        response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token),
            upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json['data']['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token),
            status=404,
            upload_files=[('invalid_name', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.tender_token),
            upload_files=[('file', 'name.doc', 'content2')],
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can update document only author')

        response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token),
            upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        key = response.json['data']['url'].split('?')[-1]

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
        self.assertEqual(doc_id, response.json['data']['id'])
        self.assertEqual('name.doc', response.json['data']['title'])

        response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token),
            'content3',
            content_type='application/msword')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        key = response.json['data']['url'].split('?')[-1]

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents/{}?{}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content3')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token),
            {'data': {'status': 'pending'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'pending')

        response = self.app.put(
            '/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(self.tender_id, self.award_id,
                                                                                   self.complaint_id, doc_id,
                                                                                   self.complaint_owner_token),
            'content4', content_type='application/msword')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents/{}?{}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content4')

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason', 'status': 'active',
                                                'cancellationOf': 'lot', 'relatedLot': self.lots[0]['id']}})
        self.assertEqual(response.status, '201 Created')

        response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token),
            upload_files=[('file', 'name.doc', 'content3')],
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         'Can update document only in active lot status')

    def test_patch_tender_award_complaint_document(self):
        response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token),
            upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json['data']['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.tender_token),
            {'data': {'description': 'document description'}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can update document only author')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token),
            {'data': {'description': 'document description'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents/{}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        self.assertEqual('document description', response.json['data']['description'])

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token),
            {'data': {'status': 'pending'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'pending')

        response = self.app.patch_json(
            '/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(self.tender_id, self.award_id,
                                                                                   self.complaint_id, doc_id,
                                                                                   self.complaint_owner_token),
            {"data": {"description": "document description2"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["description"], "document description2")

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason', 'status': 'active',
                                                'cancellationOf': 'lot', 'relatedLot': self.lots[0]['id']}})
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token),
            {'data': {'description': 'document description'}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can update document only in active lot status')


class TenderStage2UAAwardDocumentResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_tender_bids

    def setUp(self):
        super(TenderStage2UAAwardDocumentResourceTest, self).setUp()
        # Create award
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(self.tender_id),
                                      {'data': {'suppliers': [author],
                                                'status': 'pending',
                                                'bid_id': self.bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.authorization = auth

    def test_not_found(self):
        response = self.app.post('/tenders/some_id/awards/some_id/documents',
                                 status=404,
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.post('/tenders/{}/awards/some_id/documents'.format(self.tender_id),
                                 status=404,
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        response = self.app.post('/tenders/{}/awards/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token),
            status=404,
            upload_files=[('invalid_value', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.get('/tenders/some_id/awards/some_id/documents', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/awards/some_id/documents'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        response = self.app.get('/tenders/some_id/awards/some_id/documents/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/awards/some_id/documents/some_id'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        response = self.app.get('/tenders/{}/awards/{}/documents/some_id'.format(self.tender_id, self.award_id),
                                status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'document_id'}
        ])

        response = self.app.put('/tenders/some_id/awards/some_id/documents/some_id', status=404,
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.put('/tenders/{}/awards/some_id/documents/some_id'.format(self.tender_id),
                                status=404,
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        response = self.app.put('/tenders/{}/awards/{}/documents/some_id'.format(
            self.tender_id, self.award_id),
            status=404,
            upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
        ])

    def test_create_tender_award_document(self):
        response = self.app.post('/tenders/{}/awards/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token),
            upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json['data']['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name.doc', response.json['data']['title'])
        key = response.json['data']['url'].split('?')[-1]

        response = self.app.get('/tenders/{}/awards/{}/documents'.format(self.tender_id, self.award_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data'][0]['id'])
        self.assertEqual('name.doc', response.json['data'][0]['title'])

        response = self.app.get('/tenders/{}/awards/{}/documents?all=true'.format(self.tender_id, self.award_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data'][0]['id'])
        self.assertEqual('name.doc', response.json['data'][0]['title'])

        response = self.app.get('/tenders/{}/awards/{}/documents/{}?download=some_id'.format(
            self.tender_id, self.award_id, doc_id),
            status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
        ])

        response = self.app.get('/tenders/{}/awards/{}/documents/{}?{}'.format(
            self.tender_id, self.award_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 7)
        self.assertEqual(response.body, 'content')

        response = self.app.get('/tenders/{}/awards/{}/documents/{}'.format(self.tender_id, self.award_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        self.assertEqual('name.doc', response.json['data']['title'])

        self.set_status('complete')

        response = self.app.post('/tenders/{}/awards/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token),
            upload_files=[('file', 'name.doc', 'content')],
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't add document in current (complete) tender status")

    def test_put_tender_award_document(self):
        response = self.app.post('/tenders/{}/awards/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token),
            upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json['data']['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.put('/tenders/{}/awards/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, doc_id, self.tender_token),
            status=404,
            upload_files=[('invalid_name', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.put('/tenders/{}/awards/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, doc_id, self.tender_token),
            upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        key = response.json['data']['url'].split('?')[-1]

        response = self.app.get('/tenders/{}/awards/{}/documents/{}?{}'.format(
            self.tender_id, self.award_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content2')

        response = self.app.get('/tenders/{}/awards/{}/documents/{}'.format(
            self.tender_id, self.award_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        self.assertEqual('name.doc', response.json['data']['title'])

        response = self.app.put('/tenders/{}/awards/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, doc_id, self.tender_token),
            'content3',
            content_type='application/msword')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        key = response.json['data']['url'].split('?')[-1]

        response = self.app.get('/tenders/{}/awards/{}/documents/{}?{}'.format(
            self.tender_id, self.award_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content3')

        self.set_status('complete')

        response = self.app.put('/tenders/{}/awards/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, doc_id, self.tender_token),
            upload_files=[('file', 'name.doc', 'content3')],
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't update document in current (complete) tender status")

    def test_patch_tender_award_document(self):
        response = self.app.post('/tenders/{}/awards/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token),
            upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json['data']['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.patch_json('/tenders/{}/awards/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, doc_id, self.tender_token),
            {'data': {'description': 'document description'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])

        response = self.app.get('/tenders/{}/awards/{}/documents/{}'.format(
            self.tender_id, self.award_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        self.assertEqual('document description', response.json['data']['description'])

        self.set_status('complete')

        response = self.app.patch_json('/tenders/{}/awards/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, doc_id, self.tender_token),
            {'data': {'description': 'document description'}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'],
                         "Can't update document in current (complete) tender status")

    def test_create_award_document_bot(self):
        old_authorization = self.app.authorization
        self.app.authorization = ('Basic', ('bot', 'bot'))
        response = self.app.post('/tenders/{}/awards/{}/documents'.format(self.tender_id, self.award_id),
                                 upload_files=[('file', 'edr_request.yaml', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('edr_request.yaml', response.json["data"]["title"])
        if self.docservice:
            self.assertIn('Signature=', response.json["data"]["url"])
            self.assertIn('KeyID=', response.json["data"]["url"])
            self.assertNotIn('Expires=', response.json["data"]["url"])
            key = response.json["data"]["url"].split('/')[-1].split('?')[0]
            tender = self.db.get(self.tender_id)
            self.assertIn(key, tender['awards'][-1]['documents'][-1]["url"])
            self.assertIn('Signature=', tender['awards'][-1]['documents'][-1]["url"])
            self.assertIn('KeyID=', tender['awards'][-1]['documents'][-1]["url"])
            self.assertNotIn('Expires=', tender['awards'][-1]['documents'][-1]["url"])

        self.app.authorization = old_authorization

    def test_patch_not_author(self):
        authorization = self.app.authorization
        self.app.authorization = ('Basic', ('bot', 'bot'))
        response = self.app.post('/tenders/{}/awards/{}/documents'.format(self.tender_id, self.award_id),
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])

        self.app.authorization = authorization
        response = self.app.patch_json('/tenders/{}/awards/{}/documents/{}?acc_token={}'.format(self.tender_id, self.award_id, doc_id, self.tender_token),
                                       {"data": {"description": "document description"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can update document only author")
        self.app.authorization = authorization


class TenderStage2UA2LotAwardDocumentResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = 'active.qualification'
    initial_bids = test_tender_bids
    initial_lots = deepcopy(2 * test_lots)

    def setUp(self):
        super(TenderStage2UA2LotAwardDocumentResourceTest, self).setUp()
        # Create award
        bid = self.bids[0]
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(
            self.tender_id), {'data': {'suppliers': [author], 'status': 'pending',
                                       'bid_id': bid['id'], 'lotID': bid['lotValues'][0]['relatedLot']}})
        award = response.json['data']
        self.award_id = award['id']
        self.app.authorization = auth

    def test_create_tender_award_document(self):
        response = self.app.post('/tenders/{}/awards/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token),
            upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json['data']['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name.doc', response.json['data']['title'])
        key = response.json['data']['url'].split('?')[-1]

        response = self.app.get('/tenders/{}/awards/{}/documents'.format(self.tender_id, self.award_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data'][0]['id'])
        self.assertEqual('name.doc', response.json['data'][0]['title'])

        response = self.app.get('/tenders/{}/awards/{}/documents?all=true'.format(self.tender_id, self.award_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data'][0]['id'])
        self.assertEqual('name.doc', response.json['data'][0]['title'])

        response = self.app.get('/tenders/{}/awards/{}/documents/{}?download=some_id'.format(
            self.tender_id, self.award_id, doc_id),
            status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
        ])

        response = self.app.get('/tenders/{}/awards/{}/documents/{}?{}'.format(
            self.tender_id, self.award_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 7)
        self.assertEqual(response.body, 'content')

        response = self.app.get('/tenders/{}/awards/{}/documents/{}'.format(
            self.tender_id, self.award_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        self.assertEqual('name.doc', response.json['data']['title'])

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason', 'status': 'active',
                                                'cancellationOf': 'lot', 'relatedLot': self.lots[0]['id']}})
        self.assertEqual(response.status, '201 Created')

        response = self.app.post('/tenders/{}/awards/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token),
            upload_files=[('file', 'name.doc', 'content')],
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can add document only in active lot status')

    def test_put_tender_award_document(self):
        response = self.app.post('/tenders/{}/awards/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token),
            upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json['data']['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.put('/tenders/{}/awards/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, doc_id, self.tender_token),
            status=404,
            upload_files=[('invalid_name', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.put('/tenders/{}/awards/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, doc_id, self.tender_token),
            upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        key = response.json['data']['url'].split('?')[-1]

        response = self.app.get('/tenders/{}/awards/{}/documents/{}?{}'.format(
            self.tender_id, self.award_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content2')

        response = self.app.get('/tenders/{}/awards/{}/documents/{}'.format(
            self.tender_id, self.award_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        self.assertEqual('name.doc', response.json['data']['title'])

        response = self.app.put('/tenders/{}/awards/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, doc_id, self.tender_token),
            'content3',
            content_type='application/msword')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        key = response.json['data']['url'].split('?')[-1]

        response = self.app.get('/tenders/{}/awards/{}/documents/{}?{}'.format(
            self.tender_id, self.award_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content3')

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason', 'status': 'active',
                                                'cancellationOf': 'lot', 'relatedLot': self.lots[0]['id']}})
        self.assertEqual(response.status, '201 Created')

        response = self.app.put('/tenders/{}/awards/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, doc_id, self.tender_token),
            upload_files=[('file', 'name.doc', 'content3')],
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can update document only in active lot status')

    def test_patch_tender_award_document(self):
        response = self.app.post('/tenders/{}/awards/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token),
            upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json['data']['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.patch_json('/tenders/{}/awards/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, doc_id, self.tender_token),
            {'data': {'description': 'document description'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])

        response = self.app.get('/tenders/{}/awards/{}/documents/{}'.format(self.tender_id, self.award_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json['data']['id'])
        self.assertEqual('document description', response.json['data']['description'])

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason', 'status': 'active',
                                                'cancellationOf': 'lot', 'relatedLot': self.lots[0]['id']}})
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json('/tenders/{}/awards/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, doc_id, self.tender_token),
            {'data': {'description': 'document description'}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], 'Can update document only in active lot status')

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderStage2EU2LotAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EU2LotAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EU2LotAwardDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EU2LotAwardResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUAwardComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUAwardComplaintResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUAwardDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUAwardResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EULotAwardResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
