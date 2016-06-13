# -*- coding: utf-8 -*-
import unittest

from openprocurement.tender.limited.tests.base import (
    BaseTenderContentWebTest, test_tender_data, test_tender_negotiation_data,
    test_tender_negotiation_quick_data, test_organization)


class TenderAwardResourceTest(BaseTenderContentWebTest):
    initial_status = 'active'
    initial_data = test_tender_data
    initial_bids = None

    def test_create_tender_award_invalid(self):
        request_path = '/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.tender_token)
        response = self.app.post(request_path, 'data', status=415)
        self.assertEqual(response.status, '415 Unsupported Media Type')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description':
                u"Content-Type header should be one of ['application/json']", u'location': u'header', u'name': u'Content-Type'}
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
                u'Please use a mapping for this field or Identifier instance instead of unicode.']}, u'location': u'body', u'name': u'suppliers'}
        ])

        response = self.app.post_json('/tenders/some_id/awards', {'data': {
                                      'suppliers': [test_organization], 'bid_id': 'some_id'}}, status=404)
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

        response = self.app.post_json('/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': {'suppliers': [test_organization],
                                                'status': 'pending'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't create award in current (complete) tender status")

    def test_create_tender_award(self):
        request_path = '/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.tender_token)
        response = self.app.post_json(request_path, {'data': {'suppliers': [test_organization],
                                                              'subcontractingDetails': 'Details',
                                                              'status': 'pending'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        award = response.json['data']
        self.assertEqual(award['suppliers'][0]['name'], test_organization['name'])
        self.assertIn('id', award)
        self.assertIn(award['id'], response.headers['Location'])
        self.assertEqual(response.json['data']["subcontractingDetails"], "Details")

        response = self.app.get(request_path)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'][-1], award)

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award['id'], self.tender_token),
                                       {"data": {"description": "description data"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award['id'], self.tender_token),
                                       {"data": {"subcontractingDetails": "subcontractingDetails"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["subcontractingDetails"], "subcontractingDetails")

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award['id'], self.tender_token),
                                       {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'active')

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'active')

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award['id'], self.tender_token),
                                       {"data": {"status": "cancelled"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'cancelled')
        # self.assertIn('Location', response.headers)

    def test_canceling_created_award_and_create_new_one(self):
        request_path = '/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.tender_token)
        response = self.app.post_json(request_path, {'data': {'suppliers': [test_organization],
                                                              'status': 'pending'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        award = response.json['data']
        self.assertEqual(award['suppliers'][0]['name'], test_organization['name'])
        self.assertIn('id', award)
        self.assertIn(award['id'], response.headers['Location'])

        response = self.app.get(request_path)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'][-1], award)

        response = self.app.post_json('/tenders/{}/awards?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'suppliers':[test_organization], 'status': 'pending'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'][0]["description"], "Can't create new award while any (pending) award exists")

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, award['id'], self.tender_token),{"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'active')

        response = self.app.post_json('/tenders/{}/awards?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'suppliers':[test_organization], 'status': 'pending'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'][0]["description"], "Can't create new award while any (active) award exists")

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, award['id'], self.tender_token), {"data": {"status": "cancelled"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'cancelled')

        # Create new award
        response = self.app.post_json(request_path, {'data': {'suppliers': [test_organization],
                                                              'status': 'pending'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        new_award = response.json['data']
        self.assertEqual(new_award['suppliers'][0]['name'], test_organization['name'])
        self.assertIn('id', new_award)
        self.assertIn(new_award['id'], response.headers['Location'])

        # Add document to new award
        response = self.app.post('/tenders/{}/awards/{}/documents?acc_token={}'.format(
            self.tender_id, new_award['id'], self.tender_token), upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name.doc', response.json["data"]["title"])

        response = self.app.get('/tenders/{}/awards/{}/documents'.format(self.tender_id, new_award['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"][0]["id"])

        # patch new award
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, new_award['id'], self.tender_token),{"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'active')

    def test_patch_tender_award(self):
        request_path = '/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.tender_token)
        response = self.app.post_json(request_path, {'data': {'suppliers': [test_organization],
                                                              'status': u'pending', "value": {"amount": 500}}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        award = response.json['data']

        response = self.app.patch_json('/tenders/{}/awards/some_id'.format(self.tender_id),
                                       {"data": {"status": "unsuccessful"}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        response = self.app.patch_json('/tenders/some_id/awards/some_id',
                                       {"data": {"status": "unsuccessful"}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award['id'], self.tender_token),
                                       {"data": {"awardStatus": "unsuccessful"}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'], [
            {"location": "body", "name": "awardStatus", "description": "Rogue field"}
        ])

        # set/update award title
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award['id'], self.tender_token),
                                       {"data": {"title": 'award title'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['title'], 'award title')
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award['id'], self.tender_token),
                                       {"data": {"title": 'award title2'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['title'], 'award title2')

        # update supplier info
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award['id'], self.tender_token),
                                       {"data": {"suppliers": [{"name": "another supplier"}]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['suppliers'][0]['name'], 'another supplier')

        # update value
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award['id'], self.tender_token),
                                       {"data": {"value": {"amount": 499}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['value']['amount'], 499)

        # change status
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award['id'], self.tender_token),
                                       {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

        # try to update award
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award['id'], self.tender_token),
                                       {"data": {"title": 'award title'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update award in current (active) status")

        # patch status for create new award
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award['id'], self.tender_token),
                                       {"data": {"status": 'cancelled'}})
        self.assertEqual(response.status, '200 OK')

        # create new award and test other states
        response = self.app.post_json(request_path, {'data': {'suppliers': [test_organization],
                                                              'status': u'pending', "value": {"amount": 500}}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        award = response.json['data']

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award['id'], self.tender_token),
                                       {"data": {"status": "unsuccessful"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award['id'], self.tender_token),
                                       {"data": {"status": "pending"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update award in current (unsuccessful) status")

        response = self.app.post_json(request_path, {'data': {'suppliers': [test_organization],
                                                              'status': u'pending', "value": {"amount": 500}}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        award = response.json['data']
        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award['id'], self.tender_token),
                                       {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        active_award = award

        response = self.app.get(request_path)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']), 3)

        # sign contract to complete tender
        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            if i.get('complaintPeriod', {}):  # works for negotiation tender
                i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)
        response = self.app.get('/tenders/{}/contracts'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']), 2)
        contract = response.json['data'][1]
        self.assertEqual(contract['awardID'], active_award['id'])
        response = self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, contract['id'], self.tender_token),
                                       {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.get('/tenders/{}/awards/{}'.format(self.tender_id, award['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["value"]["amount"], 500)

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award['id'], self.tender_token),
                                       {"data": {"status": "active"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update award in current (complete) tender status")

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award['id'], self.tender_token),
                                       {"data": {"status": "unsuccessful"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update award in current (complete) tender status")

    def test_patch_tender_award_unsuccessful(self):
        request_path = '/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.tender_token)
        response = self.app.post_json(request_path, {'data': {'suppliers': [test_organization],
                                                              'status': u'pending', "value": {"amount": 500}}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        award = response.json['data']

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award['id'], self.tender_token),
                                       {"data": {"status": "unsuccessful"}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award['id'], self.tender_token),
                                       {"data": {"title": 'award title'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update award in current (unsuccessful) status")

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award['id'], self.tender_token),
                                       {"data": {"status": "active"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update award in current (unsuccessful) status")

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award['id'], self.tender_token),
                                       {"data": {"status": "cancelled"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update award in current (unsuccessful) status")

        response = self.app.post('/tenders/{}/awards/{}/documents?acc_token={}'.format(self.tender_id, award['id'], self.tender_token),
                                 upload_files=[('file', 'name.doc', 'content')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (unsuccessful) award status")

    def test_get_tender_award(self):
        response = self.app.post_json('/tenders/{}/awards?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'suppliers': [test_organization],
                                       'status': 'pending'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        award = response.json['data']

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


class TenderNegotiationAwardResourceTest(TenderAwardResourceTest):
    initial_data = test_tender_negotiation_data


class TenderNegotiationQuickAwardResourceTest(TenderNegotiationAwardResourceTest):
    initial_data = test_tender_negotiation_quick_data


class TenderNegotiationAwardComplaintResourceTest(BaseTenderContentWebTest):
    initial_data = test_tender_negotiation_data

    def setUp(self):
        super(TenderNegotiationAwardComplaintResourceTest, self).setUp()
        # Create award
        request_path = '/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.tender_token)
        response = self.app.post_json(request_path, {'data': {'suppliers': [test_organization],
                                                              'status': 'pending'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        award = response.json['data']
        self.award_id = award['id']

    def test_create_tender_award_complaint_invalid(self):
        response = self.app.post_json('/tenders/some_id/awards/some_id/complaints', {
                                      'data': {'title': 'complaint title', 'description': 'complaint description', 'author': test_organization}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}
        ])

        request_path = '/tenders/{}/awards/{}/complaints'.format(self.tender_id, self.award_id)

        response = self.app.post(request_path, 'data', status=415)
        self.assertEqual(response.status, '415 Unsupported Media Type')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description':
                u"Content-Type header should be one of ['application/json']", u'location': u'header', u'name': u'Content-Type'}
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

        response = self.app.post_json(request_path, {'data': {}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'author'},
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'title'},
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
                                      'data': {'author': {'identifier': 'invalid_value'}}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': {u'identifier': [
                u'Please use a mapping for this field or Identifier instance instead of unicode.']}, u'location': u'body', u'name': u'author'}
        ])

        response = self.app.post_json(request_path, {
                                      'data': {'title': 'complaint title', 'description': 'complaint description', 'author': {'identifier': {'id': 0}}}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': {u'contactPoint': [u'This field is required.'], u'identifier': {u'scheme': [u'This field is required.']}, u'name': [u'This field is required.'], u'address': [u'This field is required.']}, u'location': u'body', u'name': u'author'}
        ])

        response = self.app.post_json(request_path, {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': {
            'name': 'name', 'identifier': {'uri': 'invalid_value'}}}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': {u'contactPoint': [u'This field is required.'], u'identifier': {u'scheme': [u'This field is required.'], u'id': [u'This field is required.'], u'uri': [u'Not a well formed URL.']}, u'address': [u'This field is required.']}, u'location': u'body', u'name': u'author'}
        ])

    def test_create_tender_award_complaint(self):
        response = self.app.post_json('/tenders/{}/awards/{}/complaints'.format(self.tender_id, self.award_id), {'data': {
            'title': 'complaint title',
            'description': 'complaint description',
            'author': test_organization,
            'status': 'pending'
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']
        self.assertEqual(complaint['author']['name'], test_organization['name'])
        self.assertIn('id', complaint)
        self.assertIn(complaint['id'], response.headers['Location'])

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], 'active')

        self.set_status('unsuccessful')

        response = self.app.post_json('/tenders/{}/awards/{}/complaints'.format(
            self.tender_id, self.award_id), {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': test_organization}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add complaint in current (unsuccessful) tender status")

    def test_patch_tender_award_complaint(self):
        response = self.app.post_json('/tenders/{}/awards/{}/complaints'.format(
            self.tender_id, self.award_id), {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': test_organization}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']
        owner_token = response.json['access']['token']

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(self.tender_id, self.award_id, complaint['id'], self.tender_token), {"data": {
            "status": "cancelled",
            "cancellationReason": "reason"
        }}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Forbidden")

        response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token), {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(self.tender_id, self.award_id, complaint['id'], owner_token), {"data": {
            "title": "claim title",
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']["title"], "claim title")

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(self.tender_id, self.award_id, complaint['id'], owner_token), {"data": {
            "status": "pending"
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "pending")

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(self.tender_id, self.award_id, complaint['id'], owner_token), {"data": {
            "status": "stopping",
            "cancellationReason": "reason"
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "stopping")
        self.assertEqual(response.json['data']["cancellationReason"], "reason")

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/some_id'.format(self.tender_id, self.award_id), {"data": {"status": "resolved", "resolution": "resolution text"}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'complaint_id'}
        ])

        response = self.app.patch_json('/tenders/some_id/awards/some_id/complaints/some_id', {"data": {"status": "resolved", "resolution": "resolution text"}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(self.tender_id, self.award_id, complaint['id'], owner_token), {"data": {
            "status": "cancelled",
            "cancellationReason": "reason"
        }}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update complaint")

        response = self.app.patch_json('/tenders/{}/awards/some_id/complaints/some_id'.format(self.tender_id), {"data": {"status": "resolved", "resolution": "resolution text"}}, status=404)
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
        self.assertEqual(response.json['data']["status"], "stopping")
        self.assertEqual(response.json['data']["cancellationReason"], "reason")

        response = self.app.post_json('/tenders/{}/awards/{}/complaints'.format(
            self.tender_id, self.award_id), {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': test_organization}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']
        owner_token = response.json['access']['token']

        self.set_status('complete')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(self.tender_id, self.award_id, complaint['id'], owner_token), {"data": {
            "status": "claim",
        }}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update complaint in current (complete) tender status")

    def test_review_tender_award_complaint(self):
        for status in ['invalid', 'declined', 'satisfied']:
            self.app.authorization = ('Basic', ('broker', ''))
            response = self.app.post_json('/tenders/{}/awards/{}/complaints'.format(self.tender_id, self.award_id), {'data': {
                'title': 'complaint title',
                'description': 'complaint description',
                'author': test_organization,
                'status': 'pending'
            }})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            complaint = response.json['data']

            self.app.authorization = ('Basic', ('reviewer', ''))
            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, self.award_id, complaint['id']), {"data": {
                "decision": '{} complaint'.format(status)
            }})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.json['data']["decision"], '{} complaint'.format(status))

            if status != "invalid":
                response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, self.award_id, complaint['id']), {"data": {
                    "status": "accepted"
                }})
                self.assertEqual(response.status, '200 OK')
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.json['data']["status"], "accepted")

                response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, self.award_id, complaint['id']), {"data": {
                    "decision": 'accepted:{} complaint'.format(status)
                }})
                self.assertEqual(response.status, '200 OK')
                self.assertEqual(response.content_type, 'application/json')
                self.assertEqual(response.json['data']["decision"], 'accepted:{} complaint'.format(status))

            response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, self.award_id, complaint['id']), {"data": {
                "status": status
            }})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.json['data']["status"], status)

    def test_get_tender_award_complaint(self):
        response = self.app.post_json('/tenders/{}/awards/{}/complaints'.format(
            self.tender_id, self.award_id), {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': test_organization}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaint = response.json['data']

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}'.format(self.tender_id, self.award_id, complaint['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], complaint)

        response = self.app.get('/tenders/{}/awards/{}/complaints/some_id'.format(self.tender_id, self.award_id), status=404)
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
        response = self.app.post_json('/tenders/{}/awards/{}/complaints'.format(
            self.tender_id, self.award_id), {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': test_organization}})
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

        response = self.app.post_json('/tenders/{}/awards/{}/complaints'.format(
            self.tender_id, self.award_id), {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': test_organization}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can add complaint only in complaintPeriod")


class TenderNegotiationQuickAwardComplaintResourceTest(TenderNegotiationAwardComplaintResourceTest):
    initial_data = test_tender_negotiation_quick_data


class TenderNegotiationAwardComplaintDocumentResourceTest(BaseTenderContentWebTest):
    initial_data = test_tender_negotiation_data

    def setUp(self):
        super(TenderNegotiationAwardComplaintDocumentResourceTest, self).setUp()
        # Create award
        # Create award
        request_path = '/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.tender_token)
        response = self.app.post_json(request_path, {'data': {'suppliers': [test_organization],
                                                              'status': 'pending'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        award = response.json['data']
        self.award_id = award['id']
        # Create complaint for award
        response = self.app.post_json('/tenders/{}/awards/{}/complaints'.format(self.tender_id, self.award_id),
                                      {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': test_organization}})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']

    def test_not_found(self):
        response = self.app.post('/tenders/some_id/awards/some_id/complaints/some_id/documents', status=404, upload_files=[
                                 ('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.post('/tenders/{}/awards/some_id/complaints/some_id/documents'.format(self.tender_id), status=404, upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        response = self.app.post('/tenders/{}/awards/{}/complaints/some_id/documents'.format(self.tender_id, self.award_id), status=404, upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'complaint_id'}
        ])

        response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(self.tender_id, self.award_id, self.complaint_id, self.tender_token), status=404, upload_files=[
                                 ('invalid_value', 'name.doc', 'content')])
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

        response = self.app.get('/tenders/{}/awards/some_id/complaints/some_id/documents'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        response = self.app.get('/tenders/{}/awards/{}/complaints/some_id/documents'.format(self.tender_id, self.award_id), status=404)
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

        response = self.app.get('/tenders/{}/awards/some_id/complaints/some_id/documents/some_id'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        response = self.app.get('/tenders/{}/awards/{}/complaints/some_id/documents/some_id'.format(self.tender_id, self.award_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'complaint_id'}
        ])

        response = self.app.get('/tenders/{}/awards/{}/complaints/{}/documents/some_id'.format(self.tender_id, self.award_id, self.complaint_id), status=404)
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

        response = self.app.put('/tenders/{}/awards/some_id/complaints/some_id/documents/some_id'.format(self.tender_id), status=404,
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'award_id'}
        ])

        response = self.app.put('/tenders/{}/awards/{}/complaints/some_id/documents/some_id'.format(self.tender_id, self.award_id), status=404, upload_files=[
                                ('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'complaint_id'}
        ])

        response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/some_id'.format(
            self.tender_id, self.award_id, self.complaint_id), status=404, upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
        ])

    def test_create_tender_award_complaint_document(self):
        response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, self.tender_token), upload_files=[('file', 'name.doc', 'content')], status=403)
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

        self.set_status('complete')

        response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, self.tender_token), upload_files=[('file', 'name.doc', 'content')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (complete) tender status")

    def test_put_tender_award_complaint_document(self):
        response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token), upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(self.tender_id, self.award_id, self.complaint_id, doc_id, self.tender_token),
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
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.tender_token), upload_files=[('file', 'name.doc', 'content2')], status=403)
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

        self.set_status('complete')

        response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token), upload_files=[('file', 'name.doc', 'content3')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (complete) tender status")

    def test_patch_tender_award_complaint_document(self):
        response = self.app.post('/tenders/{}/awards/{}/complaints/{}/documents?acc_token={}'.format(
            self.tender_id, self.award_id, self.complaint_id, self.complaint_owner_token), upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(self.tender_id, self.award_id, self.complaint_id, doc_id, self.tender_token), {"data": {"description": "document description"}}, status=403)
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

        response = self.app.put('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token), 'content', content_type='application/msword', status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (pending) complaint status")

        self.set_status('complete')

        response = self.app.patch_json('/tenders/{}/awards/{}/complaints/{}/documents/{}?acc_token={}'.format(self.tender_id, self.award_id, self.complaint_id, doc_id, self.complaint_owner_token), {"data": {"description": "document description"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (complete) tender status")


class TenderNegotiationQuickAwardComplaintDocumentResourceTest(TenderNegotiationAwardComplaintDocumentResourceTest):
    initial_data = test_tender_negotiation_quick_data


class TenderAwardDocumentResourceTest(BaseTenderContentWebTest):
   initial_status = 'active'
   initial_data = test_tender_data
   initial_bids = None

   def setUp(self):
       super(TenderAwardDocumentResourceTest, self).setUp()
       # Create award
       response = self.app.post_json('/tenders/{}/awards?acc_token={}'.format(
           self.tender_id, self.tender_token), {'data': {'suppliers': [test_organization], 'status': 'pending'}})
       award = response.json['data']
       self.award_id = award['id']

   def test_not_found(self):
       response = self.app.post('/tenders/some_id/awards/some_id/documents', status=404, upload_files=[
                                ('file', 'name.doc', 'content')])
       self.assertEqual(response.status, '404 Not Found')
       self.assertEqual(response.content_type, 'application/json')
       self.assertEqual(response.json['status'], 'error')
       self.assertEqual(response.json['errors'], [
           {u'description': u'Not Found', u'location':
               u'url', u'name': u'tender_id'}
       ])

       response = self.app.post('/tenders/{}/awards/some_id/documents'.format(self.tender_id), status=404, upload_files=[('file', 'name.doc', 'content')])
       self.assertEqual(response.status, '404 Not Found')
       self.assertEqual(response.content_type, 'application/json')
       self.assertEqual(response.json['status'], 'error')
       self.assertEqual(response.json['errors'], [
           {u'description': u'Not Found', u'location':
               u'url', u'name': u'award_id'}
       ])

       response = self.app.post('/tenders/{}/awards/{}/documents?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token), status=404, upload_files=[
                                ('invalid_value', 'name.doc', 'content')])
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

       response = self.app.get('/tenders/{}/awards/{}/documents/some_id'.format(self.tender_id, self.award_id), status=404)
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

       response = self.app.put('/tenders/{}/awards/some_id/documents/some_id'.format(self.tender_id), status=404,
                               upload_files=[('file', 'name.doc', 'content2')])
       self.assertEqual(response.status, '404 Not Found')
       self.assertEqual(response.content_type, 'application/json')
       self.assertEqual(response.json['status'], 'error')
       self.assertEqual(response.json['errors'], [
           {u'description': u'Not Found', u'location':
               u'url', u'name': u'award_id'}
       ])

       response = self.app.put('/tenders/{}/awards/{}/documents/some_id'.format(
           self.tender_id, self.award_id), status=404, upload_files=[('file', 'name.doc', 'content2')])
       self.assertEqual(response.status, '404 Not Found')
       self.assertEqual(response.content_type, 'application/json')
       self.assertEqual(response.json['status'], 'error')
       self.assertEqual(response.json['errors'], [
           {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
       ])

   def test_create_tender_award_document(self):
       response = self.app.post('/tenders/{}/awards/{}/documents?acc_token={}'.format(
           self.tender_id, self.award_id, self.tender_token), upload_files=[('file', 'name.doc', 'content')])
       self.assertEqual(response.status, '201 Created')
       self.assertEqual(response.content_type, 'application/json')
       doc_id = response.json["data"]['id']
       self.assertIn(doc_id, response.headers['Location'])
       self.assertEqual('name.doc', response.json["data"]["title"])
       key = response.json["data"]["url"].split('?')[-1]

       response = self.app.get('/tenders/{}/awards/{}/documents'.format(self.tender_id, self.award_id))
       self.assertEqual(response.status, '200 OK')
       self.assertEqual(response.content_type, 'application/json')
       self.assertEqual(doc_id, response.json["data"][0]["id"])
       self.assertEqual('name.doc', response.json["data"][0]["title"])

       response = self.app.get('/tenders/{}/awards/{}/documents?all=true'.format(self.tender_id, self.award_id))
       self.assertEqual(response.status, '200 OK')
       self.assertEqual(response.content_type, 'application/json')
       self.assertEqual(doc_id, response.json["data"][0]["id"])
       self.assertEqual('name.doc', response.json["data"][0]["title"])

       response = self.app.get('/tenders/{}/awards/{}/documents/{}?download=some_id'.format(
           self.tender_id, self.award_id, doc_id), status=404)
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
       self.assertEqual(doc_id, response.json["data"]["id"])
       self.assertEqual('name.doc', response.json["data"]["title"])

       self.set_status('complete')

       response = self.app.post('/tenders/{}/awards/{}/documents?acc_token={}'.format(
           self.tender_id, self.award_id, self.tender_token), upload_files=[('file', 'name.doc', 'content')], status=403)
       self.assertEqual(response.status, '403 Forbidden')
       self.assertEqual(response.content_type, 'application/json')
       self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (complete) tender status")

   def test_create_tender_award_document_invalid(self):
       response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
           self.tender_id, self.award_id, self.tender_token),{"data": {"status": "active"}})
       self.assertEqual(response.status, '200 OK')

       response = self.app.post('/tenders/{}/awards/{}/documents?acc_token={}'.format(
           self.tender_id, self.award_id, self.tender_token), upload_files=[('file', 'name.doc', 'content')], status=403)
       self.assertEqual(response.status, '403 Forbidden')
       self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (active) award status")

       response = self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
           self.tender_id, self.award_id, self.tender_token), {"data": {"status": "cancelled"}})
       self.assertEqual(response.status, '200 OK')

       response = self.app.post('/tenders/{}/awards/{}/documents?acc_token={}'.format(
           self.tender_id, self.award_id, self.tender_token), upload_files=[('file', 'name.doc', 'content')], status=403)
       self.assertEqual(response.status, '403 Forbidden')
       self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (cancelled) award status")

   def test_put_tender_award_document(self):
       response = self.app.post('/tenders/{}/awards/{}/documents?acc_token={}'.format(
           self.tender_id, self.award_id, self.tender_token), upload_files=[('file', 'name.doc', 'content')])
       self.assertEqual(response.status, '201 Created')
       self.assertEqual(response.content_type, 'application/json')
       doc_id = response.json["data"]['id']
       self.assertIn(doc_id, response.headers['Location'])

       response = self.app.put('/tenders/{}/awards/{}/documents/{}?acc_token={}'.format(self.tender_id, self.award_id, doc_id, self.tender_token),
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
           self.tender_id, self.award_id, doc_id, self.tender_token), upload_files=[('file', 'name.doc', 'content2')])
       self.assertEqual(response.status, '200 OK')
       self.assertEqual(response.content_type, 'application/json')
       self.assertEqual(doc_id, response.json["data"]["id"])
       key = response.json["data"]["url"].split('?')[-1]

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
       self.assertEqual(doc_id, response.json["data"]["id"])
       self.assertEqual('name.doc', response.json["data"]["title"])

       response = self.app.put('/tenders/{}/awards/{}/documents/{}?acc_token={}'.format(
           self.tender_id, self.award_id, doc_id, self.tender_token), 'content3', content_type='application/msword')
       self.assertEqual(response.status, '200 OK')
       self.assertEqual(response.content_type, 'application/json')
       self.assertEqual(doc_id, response.json["data"]["id"])
       key = response.json["data"]["url"].split('?')[-1]

       response = self.app.get('/tenders/{}/awards/{}/documents/{}?{}'.format(
           self.tender_id, self.award_id, doc_id, key))
       self.assertEqual(response.status, '200 OK')
       self.assertEqual(response.content_type, 'application/msword')
       self.assertEqual(response.content_length, 8)
       self.assertEqual(response.body, 'content3')

       self.set_status('complete')

       response = self.app.put('/tenders/{}/awards/{}/documents/{}?acc_token={}'.format(
           self.tender_id, self.award_id, doc_id, self.tender_token), upload_files=[('file', 'name.doc', 'content3')], status=403)
       self.assertEqual(response.status, '403 Forbidden')
       self.assertEqual(response.content_type, 'application/json')
       self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (complete) tender status")

   def test_patch_tender_award_document(self):
       response = self.app.post('/tenders/{}/awards/{}/documents?acc_token={}'.format(
           self.tender_id, self.award_id, self.tender_token), upload_files=[('file', 'name.doc', 'content')])
       self.assertEqual(response.status, '201 Created')
       self.assertEqual(response.content_type, 'application/json')
       doc_id = response.json["data"]['id']
       self.assertIn(doc_id, response.headers['Location'])

       response = self.app.patch_json('/tenders/{}/awards/{}/documents/{}?acc_token={}'.format(self.tender_id, self.award_id, doc_id, self.tender_token), {"data": {"description": "document description"}})
       self.assertEqual(response.status, '200 OK')
       self.assertEqual(response.content_type, 'application/json')
       self.assertEqual(doc_id, response.json["data"]["id"])

       response = self.app.get('/tenders/{}/awards/{}/documents/{}'.format(
           self.tender_id, self.award_id, doc_id))
       self.assertEqual(response.status, '200 OK')
       self.assertEqual(response.content_type, 'application/json')
       self.assertEqual(doc_id, response.json["data"]["id"])
       self.assertEqual('document description', response.json["data"]["description"])

       self.set_status('complete')

       response = self.app.patch_json('/tenders/{}/awards/{}/documents/{}?acc_token={}'.format(self.tender_id, self.award_id, doc_id, self.tender_token), {"data": {"description": "document description"}}, status=403)
       self.assertEqual(response.status, '403 Forbidden')
       self.assertEqual(response.content_type, 'application/json')
       self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (complete) tender status")


class TenderAwardNegotiationDocumentResourceTest(TenderAwardDocumentResourceTest):
   initial_data = test_tender_negotiation_data


class TenderAwardNegotiationQuickDocumentResourceTest(TenderAwardNegotiationDocumentResourceTest):
   initial_data = test_tender_negotiation_quick_data


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderAwardDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderAwardResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
