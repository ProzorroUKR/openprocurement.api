# -*- coding: utf-8 -*-
import unittest

from openprocurement.tender.belowthreshold.tests.base import test_lots
from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest
)

###########
#  EU
###########


class TenderStage2UECancellationResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):

    def test_create_tender_cancellation_invalid(self):
        response = self.app.post_json('/tenders/some_id/cancellations',
                                      {'data': {'reason': 'cancellation reason'}},
                                      status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}
        ])

        request_path = '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token)

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
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'reason'},
        ])

        response = self.app.post_json(request_path, {'data': {'invalid_field': 'invalid_value'}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Rogue field', u'location':
                u'body', u'name': u'invalid_field'}
        ])

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'cancellationOf': 'lot'}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'relatedLot'}
        ])

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'cancellationOf': 'lot',
                                                'relatedLot': '0' * 32}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'relatedLot should be one of lots'], u'location': u'body', u'name': u'relatedLot'}
        ])

    def test_create_tender_cancellation(self):
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertIn('date', cancellation)
        self.assertEqual(cancellation['reasonType'], 'cancelled')
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], 'active.tendering')

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'active',
                                                'reasonType': 'unsuccessful'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reasonType'], 'unsuccessful')
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertEqual(cancellation['status'], 'active')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], 'cancelled')

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't add cancellation in current (cancelled) tender status")

    def test_patch_tender_cancellation(self):
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        old_date_status = response.json['data']['date']
        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id,
                                                                                          cancellation['id'],
                                                                                          self.tender_token),
                                       {"data": {'reasonType': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["reasonType"], "unsuccessful")

        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id,
                                                                                          cancellation['id'],
                                                                                          self.tender_token),
                                       {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")
        self.assertNotEqual(old_date_status, response.json['data']['date'])

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], 'cancelled')

        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id,
                                                                                          cancellation['id'],
                                                                                          self.tender_token),
                                       {"data": {"status": "pending"}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't update cancellation in current (cancelled) tender status")

        response = self.app.patch_json('/tenders/{}/cancellations/some_id?acc_token={}'.format(
            self.tender_id, self.tender_token), {"data": {"status": "active"}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        response = self.app.patch_json('/tenders/some_id/cancellations/some_id',
                                       {"data": {"status": "active"}},
                                       status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/cancellations/{}'.format(self.tender_id, cancellation['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")
        self.assertEqual(response.json['data']["reason"], "cancellation reason")

    def test_get_tender_cancellation(self):
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']

        response = self.app.get('/tenders/{}/cancellations/{}'.format(self.tender_id, cancellation['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], cancellation)

        response = self.app.get('/tenders/{}/cancellations/some_id'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        response = self.app.get('/tenders/some_id/cancellations/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

    def test_get_tender_cancellations(self):
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']

        response = self.app.get('/tenders/{}/cancellations'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'][0], cancellation)

        response = self.app.get('/tenders/some_id/cancellations', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])


class TenderStage2UELotCancellationResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_lots = test_lots

    def test_create_tender_cancellation(self):
        lot_id = self.lots[0]['id']
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'cancellationOf': 'lot',
                                                'relatedLot': lot_id}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'active')
        self.assertEqual(response.json['data']["status"], 'active.tendering')

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'active',
                                                'cancellationOf': 'lot',
                                                'relatedLot': lot_id}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertEqual(cancellation['status'], 'active')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'cancelled')
        self.assertEqual(response.json['data']["status"], 'cancelled')

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason'}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't add cancellation in current (cancelled) tender status")

    def test_patch_tender_cancellation(self):
        lot_id = self.lots[0]['id']
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'cancellationOf': 'lot',
                                                'relatedLot': lot_id}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']

        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id,
                                                                                          cancellation['id'],
                                                                                          self.tender_token),
                                       {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'cancelled')
        self.assertEqual(response.json['data']["status"], 'cancelled')

        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(
            self.tender_id, cancellation['id'], self.tender_token), {"data": {"status": "pending"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't update cancellation in current (cancelled) tender status")

        response = self.app.get('/tenders/{}/cancellations/{}'.format(self.tender_id, cancellation['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")
        self.assertEqual(response.json['data']["reason"], "cancellation reason")


class TenderStage2UELotsCancellationResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_lots = 2 * test_lots

    def test_create_tender_cancellation(self):
        lot_id = self.lots[0]['id']
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'cancellationOf': 'lot',
                                                'relatedLot': lot_id}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'active')
        self.assertEqual(response.json['data']["status"], 'active.tendering')

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'active',
                                                'cancellationOf': 'lot',
                                                'relatedLot': lot_id}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertEqual(cancellation['status'], 'active')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'cancelled')
        self.assertNotEqual(response.json['data']["status"], 'cancelled')

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'active',
                                                "cancellationOf": "lot",
                                                "relatedLot": lot_id}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can add cancellation only in active lot status")

    def test_patch_tender_cancellation(self):
        lot_id = self.lots[0]['id']
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'cancellationOf': 'lot',
                                                'relatedLot': lot_id}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']

        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id,
                                                                                          cancellation['id'],
                                                                                          self.tender_token),
                                       {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'cancelled')
        self.assertNotEqual(response.json['data']["status"], 'cancelled')

        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id,
                                                                                          cancellation['id'],
                                                                                          self.tender_token),
                                       {"data": {"status": "pending"}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can update cancellation only in active lot status")

        response = self.app.get('/tenders/{}/cancellations/{}'.format(self.tender_id, cancellation['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")
        self.assertEqual(response.json['data']["reason"], "cancellation reason")


class TenderStage2UECancellationDocumentResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):

    def setUp(self):
        super(TenderStage2UECancellationDocumentResourceTest, self).setUp()
        # Create cancellation
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason'}})
        cancellation = response.json['data']
        self.cancellation_id = cancellation['id']

    def test_not_found(self):
        response = self.app.post('/tenders/some_id/cancellations/some_id/documents',
                                 status=404,
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.post('/tenders/{}/cancellations/some_id/documents?acc_token={}'.format(self.tender_id,
                                                                                                   self.tender_token),
                                 status=404,
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(self.tender_id,
                                                                                              self.cancellation_id,
                                                                                              self.tender_token),
                                 status=404,
                                 upload_files=[('invalid_value', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.get('/tenders/some_id/cancellations/some_id/documents', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/cancellations/some_id/documents'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        response = self.app.get('/tenders/some_id/cancellations/some_id/documents/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/cancellations/some_id/documents/some_id'.format(self.tender_id),
                                status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        response = self.app.get('/tenders/{}/cancellations/{}/documents/some_id'.format(self.tender_id,
                                                                                        self.cancellation_id),
                                status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'document_id'}
        ])

        response = self.app.put('/tenders/some_id/cancellations/some_id/documents/some_id',
                                upload_files=[('file', 'name.doc', 'content2')],
                                status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.put('/tenders/{}/cancellations/some_id/documents/some_id?acc_token={}'.format(self.tender_id,
                                                                                                          self.tender_token),
                                upload_files=[('file', 'name.doc', 'content2')],
                                status=404)

        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        response = self.app.put('/tenders/{}/cancellations/{}/documents/some_id?acc_token={}'.format(self.tender_id,
                                                                                                     self.cancellation_id,
                                                                                                     self.tender_token),
                                status=404,
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
        ])

    def test_create_tender_cancellation_document(self):
        response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(self.tender_id,
                                                                                              self.cancellation_id,
                                                                                              self.tender_token),
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name.doc', response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.get('/tenders/{}/cancellations/{}/documents'.format(self.tender_id, self.cancellation_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"][0]["id"])
        self.assertEqual('name.doc', response.json["data"][0]["title"])

        response = self.app.get('/tenders/{}/cancellations/{}/documents?all=true'.format(self.tender_id, self.cancellation_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"][0]["id"])
        self.assertEqual('name.doc', response.json["data"][0]["title"])

        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}?download=some_id'.format(self.tender_id,
                                                                                                    self.cancellation_id,
                                                                                                    doc_id),
                                status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
        ])

        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}?{}'.format(self.tender_id,
                                                                                      self.cancellation_id,
                                                                                      doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 7)
        self.assertEqual(response.body, 'content')

        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}'.format(self.tender_id,
                                                                                   self.cancellation_id,
                                                                                   doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name.doc', response.json["data"]["title"])

        self.set_status('complete')

        response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(self.tender_id,
                                                                                              self.cancellation_id,
                                                                                              self.tender_token),
                                 upload_files=[('file', 'name.doc', 'content')],
                                 status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't add document in current (complete) tender status")

    def test_put_tender_cancellation_document(self):
        response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(self.tender_id,
                                                                                              self.cancellation_id,
                                                                                              self.tender_token),
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(self.tender_id,
                                                                                                self.cancellation_id,
                                                                                                doc_id,
                                                                                                self.tender_token),
                                status=404,
                                upload_files=[('invalid_name', 'name.doc', 'content')])

        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(self.tender_id,
                                                                                                self.cancellation_id,
                                                                                                doc_id,
                                                                                                self.tender_token),
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}?{}'.format(self.tender_id,
                                                                                      self.cancellation_id,
                                                                                      doc_id,
                                                                                      key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content2')

        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}'.format(self.tender_id,
                                                                                   self.cancellation_id,
                                                                                   doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name.doc', response.json["data"]["title"])

        response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(self.tender_id,
                                                                                                self.cancellation_id,
                                                                                                doc_id,
                                                                                                self.tender_token),
                                'content3',
                                content_type='application/msword')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}?{}'.format(self.tender_id,
                                                                                      self.cancellation_id,
                                                                                      doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content3')

        self.set_status('complete')

        response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(self.tender_id,
                                                                                                self.cancellation_id,
                                                                                                doc_id,
                                                                                                self.tender_token),
                                upload_files=[('file', 'name.doc', 'content3')],
                                status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't update document in current (complete) tender status")

    def test_patch_tender_cancellation_document(self):
        response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(self.tender_id,
                                                                                              self.cancellation_id,
                                                                                              self.tender_token),
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.patch_json('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.cancellation_id, doc_id, self.tender_token),
            {"data": {"description": "document description"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])

        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}'.format(self.tender_id,
                                                                                   self.cancellation_id,
                                                                                   doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('document description', response.json["data"]["description"])

        self.set_status('complete')

        response = self.app.patch_json('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.cancellation_id, doc_id, self.tender_token),
            {"data": {"description": "document description"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't update document in current (complete) tender status")


#########
# UA
#########


class TenderStage2UACancellationResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):

    initial_auth = ('Basic', ('broker', ''))

    def test_create_tender_cancellation_invalid(self):
        response = self.app.post_json('/tenders/some_id/cancellations',
                                      {'data': {'reason': 'cancellation reason'}},
                                      status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}
        ])

        request_path = '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token)

        response = self.app.post(request_path, 'data', status=415)
        self.assertEqual(response.status, '415 Unsupported Media Type')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description':
                u"Content-Type header should be one of ['application/json']",
             u'location': u'header', u'name': u'Content-Type'}
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
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'reason'},
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

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason', "cancellationOf": "lot"}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'relatedLot'}
        ])

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                "cancellationOf": "lot",
                                                "relatedLot": '0' * 32}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'relatedLot should be one of lots'],
             u'location': u'body',
             u'name': u'relatedLot'}
        ])

    def test_create_tender_cancellation(self):
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertEqual(cancellation['reasonType'], 'cancelled')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], 'active.tendering')

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'reasonType': 'unsuccessful',
                                                'status': 'active'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reasonType'], 'unsuccessful')
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertEqual(cancellation['status'], 'active')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], 'cancelled')

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason'}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't add cancellation in current (cancelled) tender status")

    def test_patch_tender_cancellation(self):
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']

        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id,
                                                                                          cancellation['id'],
                                                                                          self.tender_token),
                                       {"data": {'reasonType': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["reasonType"], "unsuccessful")

        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id,
                                                                                          cancellation['id'],
                                                                                          self.tender_token),
                                       {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], 'cancelled')

        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id,
                                                                                          cancellation['id'],
                                                                                          self.tender_token),
                                       {"data": {"status": "pending"}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't update cancellation in current (cancelled) tender status")

        response = self.app.patch_json('/tenders/{}/cancellations/some_id?acc_token={}'.format(self.tender_id,
                                                                                               self.tender_token),
                                       {"data": {"status": "active"}},
                                       status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        response = self.app.patch_json('/tenders/some_id/cancellations/some_id',
                                       {"data": {"status": "active"}},
                                       status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/cancellations/{}'.format(self.tender_id, cancellation['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")
        self.assertEqual(response.json['data']["reason"], "cancellation reason")

    def test_get_tender_cancellation(self):
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']

        response = self.app.get('/tenders/{}/cancellations/{}'.format(self.tender_id, cancellation['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], cancellation)

        response = self.app.get('/tenders/{}/cancellations/some_id'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        response = self.app.get('/tenders/some_id/cancellations/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

    def test_get_tender_cancellations(self):
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']

        response = self.app.get('/tenders/{}/cancellations'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'][0], cancellation)

        response = self.app.get('/tenders/some_id/cancellations', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])


class TenderStage2UALotCancellationResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_lots = test_lots
    initial_auth = ('Basic', ('broker', ''))

    def test_create_tender_cancellation(self):
        lot_id = self.lots[0]['id']
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'cancellationOf': 'lot',
                                                'relatedLot': lot_id}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'active')
        self.assertEqual(response.json['data']["status"], 'active.tendering')

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason', 'status': 'active',
                                                "cancellationOf": "lot", "relatedLot": lot_id}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertEqual(cancellation['status'], 'active')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'cancelled')
        self.assertEqual(response.json['data']["status"], 'cancelled')

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't add cancellation in current (cancelled) tender status")

    def test_patch_tender_cancellation(self):
        lot_id = self.lots[0]['id']
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'cancellationOf': 'lot',
                                                'relatedLot': lot_id}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']

        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id,
                                                                                          cancellation['id'],
                                                                                          self.tender_token),
                                       {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'cancelled')
        self.assertEqual(response.json['data']["status"], 'cancelled')

        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id,
                                                                                          cancellation['id'],
                                                                                          self.tender_token),
                                       {"data": {"status": "pending"}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't update cancellation in current (cancelled) tender status")

        response = self.app.get('/tenders/{}/cancellations/{}'.format(self.tender_id, cancellation['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")
        self.assertEqual(response.json['data']["reason"], "cancellation reason")


class TenderStage2UALotsCancellationResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_lots = 2 * test_lots
    initial_auth = ('Basic', ('broker', ''))

    def test_create_tender_cancellation(self):
        lot_id = self.lots[0]['id']
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'cancellationOf': 'lot',
                                                'relatedLot': lot_id}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'active')
        self.assertEqual(response.json['data']["status"], 'active.tendering')

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason', 'status': 'active',
                                                'cancellationOf': 'lot', 'relatedLot': lot_id}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertEqual(cancellation['status'], 'active')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'cancelled')
        self.assertNotEqual(response.json['data']["status"], 'cancelled')

        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason', 'status': 'active',
                                                'cancellationOf': 'lot', 'relatedLot': lot_id}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can add cancellation only in active lot status")

    def test_patch_tender_cancellation(self):
        lot_id = self.lots[0]['id']
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'cancellationOf': 'lot',
                                                'relatedLot': lot_id}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']

        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id,
                                                                                          cancellation['id'],
                                                                                          self.tender_token),
                                       {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'cancelled')
        self.assertNotEqual(response.json['data']["status"], 'cancelled')

        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id,
                                                                                          cancellation['id'],
                                                                                          self.tender_token),
                                       {"data": {"status": "pending"}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can update cancellation only in active lot status")

        response = self.app.get('/tenders/{}/cancellations/{}'.format(self.tender_id, cancellation['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")
        self.assertEqual(response.json['data']["reason"], "cancellation reason")


class TenderStage2UACancellationDocumentResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):

    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(TenderStage2UACancellationDocumentResourceTest, self).setUp()
        # Create cancellation
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason'}})
        cancellation = response.json['data']
        self.cancellation_id = cancellation['id']

    def test_not_found(self):
        response = self.app.post('/tenders/some_id/cancellations/some_id/documents',
                                 status=404, upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.post('/tenders/{}/cancellations/some_id/documents'.format(self.tender_id),
                                 status=404,
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(self.tender_id,
                                                                                              self.cancellation_id,
                                                                                              self.tender_token),
                                 status=404, upload_files=[('invalid_value', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.get('/tenders/some_id/cancellations/some_id/documents', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/cancellations/some_id/documents'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        response = self.app.get('/tenders/some_id/cancellations/some_id/documents/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/cancellations/some_id/documents/some_id'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        response = self.app.get('/tenders/{}/cancellations/{}/documents/some_id'.format(self.tender_id,
                                                                                        self.cancellation_id),
                                status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'document_id'}
        ])

        response = self.app.put('/tenders/some_id/cancellations/some_id/documents/some_id', status=404,
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.put('/tenders/{}/cancellations/some_id/documents/some_id'.format(self.tender_id),
                                status=404, upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        response = self.app.put('/tenders/{}/cancellations/{}/documents/some_id'.format(self.tender_id,
                                                                                        self.cancellation_id),
                                status=404,
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
        ])

    def test_create_tender_cancellation_document(self):
        response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(self.tender_id,
                                                                                              self.cancellation_id,
                                                                                              self.tender_token),
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name.doc', response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.get('/tenders/{}/cancellations/{}/documents'.format(self.tender_id, self.cancellation_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"][0]["id"])
        self.assertEqual('name.doc', response.json["data"][0]["title"])

        response = self.app.get('/tenders/{}/cancellations/{}/documents?all=true'.format(self.tender_id,
                                                                                         self.cancellation_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"][0]["id"])
        self.assertEqual('name.doc', response.json["data"][0]["title"])

        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}?download=some_id'.format(
            self.tender_id, self.cancellation_id, doc_id),
            status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
        ])

        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}?{}'.format(self.tender_id,
                                                                                      self.cancellation_id,
                                                                                      doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 7)
        self.assertEqual(response.body, 'content')

        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}'.format(self.tender_id,
                                                                                   self.cancellation_id,
                                                                                   doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name.doc', response.json["data"]["title"])

        self.set_status('complete')

        response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(self.tender_id,
                                                                                              self.cancellation_id,
                                                                                              self.tender_token),
                                 upload_files=[('file', 'name.doc', 'content')],
                                 status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't add document in current (complete) tender status")

    def test_put_tender_cancellation_document(self):
        response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(self.tender_id,
                                                                                              self.cancellation_id,
                                                                                              self.tender_token),
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(self.tender_id,
                                                                                                self.cancellation_id,
                                                                                                doc_id,
                                                                                                self.tender_token),
                                status=404,
                                upload_files=[('invalid_name', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(self.tender_id,
                                                                                                self.cancellation_id,
                                                                                                doc_id,
                                                                                                self.tender_token),
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}?{}'.format(self.tender_id,
                                                                                      self.cancellation_id,
                                                                                      doc_id,
                                                                                      key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content2')

        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}'.format(self.tender_id,
                                                                                   self.cancellation_id,
                                                                                   doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name.doc', response.json["data"]["title"])

        response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(self.tender_id,
                                                                                                self.cancellation_id,
                                                                                                doc_id,
                                                                                                self.tender_token),
                                'content3',
                                content_type='application/msword')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}?{}'.format(self.tender_id,
                                                                                      self.cancellation_id,
                                                                                      doc_id,
                                                                                      key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content3')

        self.set_status('complete')

        response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(self.tender_id,
                                                                                                self.cancellation_id,
                                                                                                doc_id,
                                                                                                self.tender_token),
                                upload_files=[('file', 'name.doc', 'content3')],
                                status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't update document in current (complete) tender status")

    def test_patch_tender_cancellation_document(self):
        response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(self.tender_id,
                                                                                              self.cancellation_id,
                                                                                              self.tender_token),
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.patch_json('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.cancellation_id, doc_id, self.tender_token),
            {"data": {"description": "document description"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])

        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}'.format(self.tender_id,
                                                                                   self.cancellation_id,
                                                                                   doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('document description', response.json["data"]["description"])

        self.set_status('complete')

        response = self.app.patch_json('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.cancellation_id, doc_id, self.tender_token),
            {"data": {"description": "document description"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't update document in current (complete) tender status")



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderStage2UECancellationResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UELotCancellationResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UELotsCancellationResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UECancellationDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UACancellationResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UALotCancellationResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UALotsCancellationResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UACancellationDocumentResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
