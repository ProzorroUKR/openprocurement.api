# -*- coding: utf-8 -*-
import unittest

from openprocurement.tender.competitivedialogue.tests.base import (BaseCompetitiveDialogUAContentWebTest,
                                                                   BaseCompetitiveDialogEUContentWebTest,
                                                                   test_lots as base_test_lots)

test_lots = base_test_lots

class CompetitiveDialogUACancellationResourceTest(BaseCompetitiveDialogUAContentWebTest):

    def test_create_tender_cancellation_invalid(self):
        """
          Try cancel dialog
        """
        # Try cancel dialog with bad tender_id
        response = self.app.post_json('/tenders/some_id/cancellations',
                                      {'data': {'reason': 'cancellation reason'}},
                                      status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}
        ])

        request_path = '/tenders/{}/cancellations?acc_token={}'.format(
            self.tender_id, self.tender_token)

        # Try cancel dialog without content type
        response = self.app.post(request_path, 'data', status=415)
        self.assertEqual(response.status, '415 Unsupported Media Type')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u"Content-Type header should be one of ['application/json']",
             u'location': u'header',
             u'name': u'Content-Type'}
        ])

        # Try cancel dialog with bad json
        response = self.app.post(request_path, 'data', content_type='application/json', status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'No JSON object could be decoded',
                u'location': u'body', u'name': u'data'}
        ])

        # Try cancel dialog without data
        response = self.app.post_json(request_path, 'data', status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Data not available',
                u'location': u'body', u'name': u'data'}
        ])

        # Try cancel dialog without data in json
        response = self.app.post_json(request_path, {'not_data': {}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Data not available',
                u'location': u'body', u'name': u'data'}
        ])

        # Try cancel dialog without required fields
        response = self.app.post_json(request_path, {'data': {}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'reason'},
        ])

        # Try cancel dialog with rouge filed
        response = self.app.post_json(request_path, {'data': {'invalid_field': 'invalid_value'}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Rogue field', u'location':
                u'body', u'name': u'invalid_field'}
        ])

        # Try cancel dialog with required filed(description)
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'cancellationOf': 'lot'}
                                       },
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'relatedLot'}
        ])

        # Try cancel lot with bad lot_id
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'cancellationOf': 'lot',
                                                'relatedLot': '0' * 32}
                                       },
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'relatedLot should be one of lots'], u'location': u'body', u'name': u'relatedLot'}
        ])

    def test_create_tender_cancellation(self):
        """
          Test cancel dialog
        """
        # Add reason of canceling dialog
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reasonType'], 'cancelled')
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        # Get dialog
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], 'active.tendering')

        # Set status, reasonType, reason to dialog
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

        # Get cancel dialog
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], 'cancelled')

        # Try add reason when dialog is cancel
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], "Can't add cancellation in current (cancelled) tender status")

    def test_patch_tender_cancellation(self):
        """
          Test path tender cancellation
        """
        # Create cancel object in dialog
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']

        # Add reasonType to dialog cancel object
        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id,
                                                                                          cancellation['id'],
                                                                                          self.tender_token),
                                       {"data": {'reasonType': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["reasonType"], "unsuccessful")

        # Add status to dialog cancel object
        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id,
                                                                                          cancellation['id'],
                                                                                          self.tender_token),
                                       {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")

        # Get dialog, and check status
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], 'cancelled')

        # Try update cancellation when status dialog cancelled
        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id,
                                                                                          cancellation['id'],
                                                                                          self.tender_token),
                                       {"data": {"status": "pending"}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update cancellation in current (cancelled) tender status")

        # Try set status active in cancel object by bad cancellation_id
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

        # Try set status active in cancel object by bad tender_id
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

        # Get cancel dialog
        response = self.app.get('/tenders/{}/cancellations/{}'.format(self.tender_id, cancellation['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")
        self.assertEqual(response.json['data']["reason"], "cancellation reason")

    def test_get_tender_cancellation(self):
        """
          Get tender cancellation
        """

        # Set reason for cancellation
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']

        # Get cancellation
        response = self.app.get('/tenders/{}/cancellations/{}'.format(self.tender_id, cancellation['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], cancellation)

        # Try get cancellation by bad cancellation_id
        response = self.app.get('/tenders/{}/cancellations/some_id'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        # Try get cancellation by bad dialog id
        response = self.app.get('/tenders/some_id/cancellations/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

    def test_get_tender_cancellations(self):
        """
          Get tender Cancellations
        """

        # Create dialog cancellation
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']

        # Get dialog cancellations by dialog_id
        response = self.app.get('/tenders/{}/cancellations'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'][0], cancellation)

        # Get dialog cancellations by bad dialog_id
        response = self.app.get('/tenders/some_id/cancellations', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])


class CompetitiveDialogUALotCancellationResourceTest(BaseCompetitiveDialogUAContentWebTest):
    initial_lots = test_lots

    def test_create_tender_cancellation(self):
        """
          Test create tender cancellation with lots
        """
        lot_id = self.initial_lots[0]['id']
        # Create cancellation with reason for lot
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token), {'data': {
            'reason': 'cancellation reason',
            "cancellationOf": "lot",
            "relatedLot": lot_id
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        # Get cancellations by dialog id
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'active')
        self.assertEqual(response.json['data']['status'], 'active.tendering')

        # Activate cancellation by dialog id
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'active',
                                                "cancellationOf": "lot",
                                                "relatedLot": lot_id}
                                       })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertEqual(cancellation['status'], 'active')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        # Get dialog and check status
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'cancelled')
        self.assertEqual(response.json['data']["status"], 'cancelled')

        # Try add another cancellation in dialog which status is cancel
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], "Can't add cancellation in current (cancelled) tender status")

    def test_patch_tender_cancellation(self):
        """
          Test path tender cancellation
        """

        lot_id = self.initial_lots[0]['id']

        # Add cancellation for lot
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'cancellationOf': 'lot',
                                                'relatedLot': lot_id}
                                       })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']

        # Activate cancellation
        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(
            self.tender_id, cancellation['id'], self.tender_token), {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")

        # Get cancellation check status
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]['status'], 'cancelled')
        self.assertEqual(response.json['data']['status'], 'cancelled')

        # Try update cancellation, when dialog has status cancelled
        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id,
                                                                                          cancellation['id'],
                                                                                          self.tender_token),
                                       {"data": {"status": "pending"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update cancellation in current (cancelled) tender status")

        # Get cancellation, and check reason, status
        response = self.app.get('/tenders/{}/cancellations/{}'.format(self.tender_id, cancellation['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")
        self.assertEqual(response.json['data']["reason"], "cancellation reason")


class CompetitiveDialogUALotsCancellationResourceTest(BaseCompetitiveDialogUAContentWebTest):
    initial_lots = 2 * test_lots

    def test_create_tender_cancellation(self):
        """
          Test create tender cancellation with lots
        """
        lot_id = self.initial_lots[0]['id']
        # Create cancellation for lot
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'cancellationOf': 'lot',
                                                'relatedLot': lot_id}
                                       })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        # Get tender and check status
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'active')
        self.assertEqual(response.json['data']["status"], 'active.tendering')

        # Create new cancellation and set status activate
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'active',
                                                'cancellationOf': 'lot',
                                                'relatedLot': lot_id}
                                       })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertEqual(cancellation['status'], 'active')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        # Get dialog and check that status is cancelled, and lot are cancelled to
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'cancelled')
        self.assertNotEqual(response.json['data']["status"], 'cancelled')

        # Try create another cancellation
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'active',
                                                "cancellationOf": "lot",
                                                "relatedLot": lot_id}
                                       },
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can add cancellation only in active lot status")

    def test_patch_tender_cancellation(self):
        """
          Test path tender cancellation with lots
        """
        lot_id = self.initial_lots[0]['id']
        # Create cancellation, which related on lot
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                "cancellationOf": "lot",
                                                "relatedLot": lot_id}
                                       })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']

        # Set cancellation status active
        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id,
                                                                                          cancellation['id'],
                                                                                          self.tender_token),
                                       {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")

        # Get dialog, and check status
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'cancelled')
        self.assertNotEqual(response.json['data']["status"], 'cancelled')

        # Try edit cancellation status
        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id,
                                                                                          cancellation['id'],
                                                                                          self.tender_token),
                                       {"data": {"status": "pending"}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can update cancellation only in active lot status")

        # Get cancellation, check status and reason
        response = self.app.get('/tenders/{}/cancellations/{}'.format(self.tender_id, cancellation['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")
        self.assertEqual(response.json['data']["reason"], "cancellation reason")


class CompetitiveDialogUACancellationDocumentResourceTest(BaseCompetitiveDialogUAContentWebTest):

    def setUp(self):
        super(CompetitiveDialogUACancellationDocumentResourceTest, self).setUp()
        # Create cancellation
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason'}})
        cancellation = response.json['data']
        self.cancellation_id = cancellation['id']

    def test_not_found(self):
        """
            Test add cancellation document with wrong params
        """

        # Try add document to cancellation by bad dialog id
        response = self.app.post('/tenders/some_id/cancellations/some_id/documents', status=404,
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        # Try add cancellation document by bad cancellation id
        response = self.app.post('/tenders/{}/cancellations/some_id/documents?acc_token={}'.format(self.tender_id,
                                                                                                   self.tender_token),
                                 status=404, upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        # Try add document without description
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

        # Try get document by bad dialog id
        response = self.app.get('/tenders/some_id/cancellations/some_id/documents', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        # Try get document by bad cancellation id
        response = self.app.get('/tenders/{}/cancellations/some_id/documents'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        # Try get dialog token by bad dialog id, cancellation id, document id
        response = self.app.get('/tenders/some_id/cancellations/some_id/documents/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        # Try get document by bad document id
        response = self.app.get('/tenders/{}/cancellations/some_id/documents/some_id'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        # Try get document with bad document id
        response = self.app.get('/tenders/{}/cancellations/{}/documents/some_id'.format(self.tender_id,
                                                                                        self.cancellation_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'document_id'}
        ])

        # Try put document with bad dialog id, cancellation id, document id
        response = self.app.put('/tenders/some_id/cancellations/some_id/documents/some_id', status=404, upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        # Try put document with bad cancellation id and document id
        response = self.app.put('/tenders/{}/cancellations/some_id/documents/some_id?acc_token={}'.format(self.tender_id,
                                                                                                          self.tender_token),
                                status=404, upload_files=[('file', 'name.doc', 'content2')])

        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        # Try put document by bad document id, and ok dialog id and cancellation id
        response = self.app.put('/tenders/{}/cancellations/{}/documents/some_id?acc_token={}'.format(self.tender_id,
                                                                                                     self.cancellation_id,
                                                                                                     self.tender_token),
                                status=404, upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
        ])

    def test_create_tender_cancellation_document(self):
        """
          Test create dialog cancellation document
        """

        # Create cancellation document, and check response fields
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

        # Get cancellation documents by dialog id, and cancellation id
        response = self.app.get('/tenders/{}/cancellations/{}/documents'.format(self.tender_id, self.cancellation_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"][0]["id"])
        self.assertEqual('name.doc', response.json["data"][0]["title"])

        # Get cancellation documents by dialog id, and cancellation id with uri param all=true
        response = self.app.get('/tenders/{}/cancellations/{}/documents?all=true'.format(self.tender_id,
                                                                                         self.cancellation_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"][0]["id"])
        self.assertEqual('name.doc', response.json["data"][0]["title"])

        # Try get cancellation documents by dialog id, and cancellation id with uri param download=some_id
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

        # Get cancellation document with by dialog id, cancellation id and key
        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}?{}'.format(
            self.tender_id, self.cancellation_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 7)
        self.assertEqual(response.body, 'content')

        # Get cancellation document, by dialog id, cancellation id, and document id
        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}'.format(self.tender_id,
                                                                                   self.cancellation_id,
                                                                                   doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name.doc', response.json["data"]["title"])

        self.set_status('complete')  # Set dialog status to complete

        # Try add cancellation document when dialog status is complete
        response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(self.tender_id,
                                                                                              self.cancellation_id,
                                                                                              self.tender_token),
                                 upload_files=[('file', 'name.doc', 'content')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (complete) tender status")

    def test_put_tender_cancellation_document(self):
        """
          Test put dialog cancellation document
        """
        # Create document and save doc_id
        response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(self.tender_id,
                                                                                              self.cancellation_id,
                                                                                              self.tender_token),
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])

        # Try put document with invalid param name
        response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(self.tender_id,
                                                                                                self.cancellation_id,
                                                                                                doc_id,
                                                                                                self.tender_token),
                                status=404, upload_files=[('invalid_name', 'name.doc', 'content')])

        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        # Put document
        response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(self.tender_id,
                                                                                                self.cancellation_id,
                                                                                                doc_id,
                                                                                                self.tender_token),
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = response.json["data"]["url"].split('?')[-1]

        # Get document which we put before and check fields
        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}?{}'.format(self.tender_id,
                                                                                      self.cancellation_id,
                                                                                      doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content2')

        # Get document by dialog id, cancellation id and document id
        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}'.format(self.tender_id,
                                                                                   self.cancellation_id,
                                                                                   doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name.doc', response.json["data"]["title"])

        # Put document
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

        # Get document which we put before and check response
        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}?{}'.format(
            self.tender_id, self.cancellation_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content3')

        self.set_status('complete')  # Set dialog status to complete

        # Try put document when dialog status is complete
        response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.cancellation_id, doc_id, self.tender_token), upload_files=[('file', 'name.doc', 'content3')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (complete) tender status")

    def test_patch_tender_cancellation_document(self):
        """
          Test path dialog cancellation document
        """
        # Create cancellation document, and save doc_id
        response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(self.tender_id,
                                                                                              self.cancellation_id,
                                                                                              self.tender_token),
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])

        # Update description for cancellation document
        response = self.app.patch_json('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(self.tender_id,
                                                                                                       self.cancellation_id,
                                                                                                       doc_id,
                                                                                                       self.tender_token),
                                       {"data": {"description": "document description"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])

        # Get cancellation document and check description
        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}'.format(self.tender_id,
                                                                                   self.cancellation_id,
                                                                                   doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('document description', response.json["data"]["description"])

        self.set_status('complete')  # Set dialog status to complete

        # Try update cancellation document when dialog status is complete
        response = self.app.patch_json('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(self.tender_id,
                                                                                                       self.cancellation_id,
                                                                                                       doc_id,
                                                                                                       self.tender_token),
                                       {"data": {"description": "document description"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (complete) tender status")


class CompetitiveDialogEUCancellationResourceTest(BaseCompetitiveDialogEUContentWebTest):

    initial_auth = ('Basic', ('broker', ''))

    def test_create_tender_cancellation_invalid(self):
        """
          Test create invalid dialog cancellation
        """

        # Try create cancellation without required fields
        response = self.app.post_json('/tenders/some_id/cancellations',
                                      {'data': {'reason': 'cancellation reason'}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'tender_id'}
        ])

        request_path = '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token)

        # Try create cancellation with bad content_type
        response = self.app.post(request_path, 'data', status=415)
        self.assertEqual(response.status, '415 Unsupported Media Type')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description':
                u"Content-Type header should be one of ['application/json']", u'location': u'header', u'name': u'Content-Type'}
        ])

        # Try create cancellation with bad json
        response = self.app.post(request_path, 'data', content_type='application/json', status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'No JSON object could be decoded',
                u'location': u'body', u'name': u'data'}
        ])

        # Try create cancellation with bad data
        response = self.app.post_json(request_path, 'data', status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Data not available',
                u'location': u'body', u'name': u'data'}
        ])

        # Try create cancellation without data object in json
        response = self.app.post_json(request_path, {'not_data': {}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Data not available',
                u'location': u'body', u'name': u'data'}
        ])

        # Try create cancellation without required fields
        response = self.app.post_json(request_path, {'data': {}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'reason'},
        ])

        # Try create cancellation with invalid_field
        response = self.app.post_json(request_path, {'data': {'invalid_field': 'invalid_value'}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Rogue field', u'location':
                u'body', u'name': u'invalid_field'}
        ])

        # Try create cancellation without required field description
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'cancellationOf': 'lot'}
                                       },
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'relatedLot'}
        ])

        # Try create cancellation with bad relatedLot field
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'cancellationOf': 'lot',
                                                'relatedLot': '0' * 32}
                                       }, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'relatedLot should be one of lots'], u'location': u'body', u'name': u'relatedLot'}
        ])

    def test_create_tender_cancellation(self):
        """
          Test create dialog cancellation
        """
        # Create cancellation with reason, and check fields
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'reason': 'cancellation reason'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertEqual(cancellation['reasonType'], 'cancelled')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        # Get dialog and check field status
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], 'active.tendering')

        # Create cancellation with reason, reasontType, and status
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

        # Get tender and check status, must be cancelled
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], 'cancelled')

        # Try change reason on cancellation
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason'}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add cancellation in current (cancelled) tender status")

    def test_patch_tender_cancellation(self):
        """
          Test path dialog cancellation
        """
        # Create dialog cancellation with field reson
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']

        # Edit cancellation by id
        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id,
                                                                                          cancellation['id'],
                                                                                          self.tender_token),
                                       {"data": {'reasonType': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["reasonType"], "unsuccessful")

        # Set cancellation field to active
        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id,
                                                                                          cancellation['id'],
                                                                                          self.tender_token),
                                       {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")

        # Get dialog, and check status
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], 'cancelled')

        # Try edit cancellation, when dialog cancelled
        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id,
                                                                                          cancellation['id'],
                                                                                          self.tender_token),
                                       {"data": {"status": "pending"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update cancellation in current (cancelled) tender status")

        # Try edit cancellation with bad cancellation id
        response = self.app.patch_json('/tenders/{}/cancellations/some_id?acc_token={}'.format(self.tender_id,
                                                                                               self.tender_token),
                                       {"data": {"status": "active"}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        # Try edit cancellation with bad tender id
        response = self.app.patch_json('/tenders/some_id/cancellations/some_id', {"data": {"status": "active"}},
                                       status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        # Get cancellation and check fields
        response = self.app.get('/tenders/{}/cancellations/{}'.format(self.tender_id, cancellation['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")
        self.assertEqual(response.json['data']["reason"], "cancellation reason")

    def test_get_tender_cancellation(self):
        """
          Test get dialog cancellation
        """

        # Create cancellation with fields reason
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']

        # Get cancellation by cancellation id, and check field
        response = self.app.get('/tenders/{}/cancellations/{}'.format(self.tender_id, cancellation['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], cancellation)

        # Try get cancellation by bad cancellation id
        response = self.app.get('/tenders/{}/cancellations/some_id'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        # Try get cancellation by bad dialog id
        response = self.app.get('/tenders/some_id/cancellations/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

    def test_get_tender_cancellations(self):
        """
          Test get dialog cancellations
        """
        # Create cancellation with field reason
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason'}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']

        # Get cancellations, by dialog id
        response = self.app.get('/tenders/{}/cancellations'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'][0], cancellation)

        # Try get cancellation by bad dialog id
        response = self.app.get('/tenders/some_id/cancellations', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])


class CompetitiveDialogEULotCancellationResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_lots = test_lots

    initial_auth = ('Basic', ('broker', ''))

    def test_create_tender_cancellation(self):
        """
          Test create cancellation with link on lot
        """
        lot_id = self.initial_lots[0]['id']

        # Create cancellation with ling on lot, and check response fields
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'cancellationOf': 'lot',
                                                'relatedLot': lot_id}}
                                      )
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        # Get dialog and check lot status, and dialog status
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'active')
        self.assertEqual(response.json['data']["status"], 'active.tendering')

        # Create cancellation with link on lot. Fields reason, status, cancellationOf, relatedLot
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'active',
                                                "cancellationOf": "lot",
                                                "relatedLot": lot_id}
                                       })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertEqual(cancellation['status'], 'active')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        # Get dialog and check status, dialog, lot
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'cancelled')
        self.assertEqual(response.json['data']["status"], 'cancelled')

        # Try add new cancellation, when status dialog is cancelled
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason'}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add cancellation in current (cancelled) tender status")

    def test_patch_tender_cancellation(self):
        """
          Test path dialog cancellation with link on lot
        """
        lot_id = self.initial_lots[0]['id']
        # Create cancellation with link on lot, fields reason, relatedLot, cancellationOf
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'cancellationOf': 'lot',
                                                'relatedLot': lot_id}
                                       })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']

        # Edit cancellation by cancellation id, change status to active.
        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id,
                                                                                          cancellation['id'],
                                                                                          self.tender_token),
                                       {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")

        # Get dialog by dialog id, and check status
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'cancelled')
        self.assertEqual(response.json['data']["status"], 'cancelled')

        # Try edit cancellation when dialog status is cancelled
        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id,
                                                                                          cancellation['id'],
                                                                                          self.tender_token),
                                       {"data": {"status": "pending"}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update cancellation in current (cancelled) tender status")

        # Get cancellation then check status, and reason
        response = self.app.get('/tenders/{}/cancellations/{}'.format(self.tender_id, cancellation['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")
        self.assertEqual(response.json['data']["reason"], "cancellation reason")


class CompetitiveDialogEULotsCancellationResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_lots = 2 * test_lots
    initial_auth = ('Basic', ('broker', ''))

    def test_create_tender_cancellation(self):
        """
          Test create dialog cancellation when lots more then one
        """

        lot_id = self.initial_lots[0]['id']
        # Create cancellation with link on lot, fields reason, cancellationOf, relatedLot
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'cancellationOf': 'lot',
                                                'relatedLot': lot_id}
                                       })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        # Get dialog and check dialog status, and lot status
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'active')
        self.assertEqual(response.json['data']["status"], 'active.tendering')

        # Create new cancellation, with link on lot. Fields reason, status, cancellationId, relatedLot
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'active',
                                                'cancellationOf': 'lot',
                                                'relatedLot': lot_id
                                                }
                                       })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']
        self.assertEqual(cancellation['reason'], 'cancellation reason')
        self.assertEqual(cancellation['status'], 'active')
        self.assertIn('id', cancellation)
        self.assertIn(cancellation['id'], response.headers['Location'])

        # Get dialog and check dialog, lot status
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'cancelled')
        self.assertNotEqual(response.json['data']["status"], 'cancelled')

        # Try create new cancellation when dialog status cancelled
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'active',
                                                'cancellationOf': 'lot',
                                                'relatedLot': lot_id}
                                       }, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can add cancellation only in active lot status")

    def test_patch_tender_cancellation(self):
        """
          Test patch dialog cancellation with losts
        """

        lot_id = self.initial_lots[0]['id']
        # Create cancellation fields resaon, cancellationOf, relatedLot
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'cancellationOf': 'lot',
                                                'relatedLot': lot_id}
                                       })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        cancellation = response.json['data']

        # Change cancellation status to active
        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id,
                                                                                          cancellation['id'],
                                                                                          self.tender_token),
                                       {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")

        # Get dialog, and check status must be cancelled
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lots'][0]["status"], 'cancelled')
        self.assertNotEqual(response.json['data']["status"], 'cancelled')

        # Try edit cancellation when dialog status is cancelled
        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation['id'], self.tender_token), {"data": {"status": "pending"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can update cancellation only in active lot status")

        # Get cancellation and dialog and lot status
        response = self.app.get('/tenders/{}/cancellations/{}'.format(self.tender_id, cancellation['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")
        self.assertEqual(response.json['data']["reason"], "cancellation reason")


class CompetitiveDialogEUCancellationDocumentResourceTest(BaseCompetitiveDialogEUContentWebTest):

    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(CompetitiveDialogEUCancellationDocumentResourceTest, self).setUp()
        # Create cancellation
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason'}})
        cancellation = response.json['data']
        self.cancellation_id = cancellation['id']

    def test_not_found(self):
        """
          Test add cancellation document with wrong params
        """

        # Try add document to cancellation by bad dialog id
        response = self.app.post('/tenders/some_id/cancellations/some_id/documents', status=404,
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        # Try add document to cancellation by bad dialog id
        response = self.app.post('/tenders/{}/cancellations/some_id/documents'.format(self.tender_id),status=404,
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        # Try add document to cancellation with bad token
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

        # Try get cancellation documents by wrong dialog id
        response = self.app.get('/tenders/some_id/cancellations/some_id/documents', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        # Try get cancellation documents by wrong cancellation id
        response = self.app.get('/tenders/{}/cancellations/some_id/documents'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        # Try get cancellation documents bt bad document id
        response = self.app.get('/tenders/some_id/cancellations/some_id/documents/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        # Try get document by ok dialog id, and bad cancellation id, document id
        response = self.app.get('/tenders/{}/cancellations/some_id/documents/some_id'.format(self.tender_id),
                                status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        # Try get document bu ok dialog id and cancellation id, but bad document id
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

        # Try put document by bad dialog id, cancellation id, document id
        response = self.app.put('/tenders/some_id/cancellations/some_id/documents/some_id', status=404,
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        # Try put document by bad cancellation id and document id, but ok dialog id
        response = self.app.put('/tenders/{}/cancellations/some_id/documents/some_id'.format(self.tender_id),
                                status=404, upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'cancellation_id'}
        ])

        # Try put document with bad document id, but ok document id, cancellation id,
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
        """
          Test create dialog cancellation document
        """
        # Add document, and check response
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

        # Get documents which we make before
        response = self.app.get('/tenders/{}/cancellations/{}/documents'.format(self.tender_id, self.cancellation_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"][0]["id"])
        self.assertEqual('name.doc', response.json["data"][0]["title"])

        # Get documents with url args
        response = self.app.get('/tenders/{}/cancellations/{}/documents?all=true'.format(self.tender_id,
                                                                                         self.cancellation_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"][0]["id"])
        self.assertEqual('name.doc', response.json["data"][0]["title"])

        # Try get document with url param download
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

        # Get document with key
        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}?{}'.format(
            self.tender_id, self.cancellation_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 7)
        self.assertEqual(response.body, 'content')

        # Get document by document id
        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}'.format(
            self.tender_id, self.cancellation_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name.doc', response.json["data"]["title"])

        self.set_status('complete')  # Set status complete for dialog

        # Try add document when dialog status is complete
        response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(self.tender_id,
                                                                                              self.cancellation_id,
                                                                                              self.tender_token),
                                 upload_files=[('file', 'name.doc', 'content')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (complete) tender status")

    def test_put_tender_cancellation_document(self):
        response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
            self.tender_id, self.cancellation_id, self.tender_token), upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(self.tender_id, self.cancellation_id, doc_id, self.tender_token),
                                status=404,
                                upload_files=[('invalid_name', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.cancellation_id, doc_id, self.tender_token), upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}?{}'.format(
            self.tender_id, self.cancellation_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content2')

        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}'.format(
            self.tender_id, self.cancellation_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name.doc', response.json["data"]["title"])

        response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.cancellation_id, doc_id, self.tender_token), 'content3', content_type='application/msword')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}?{}'.format(
            self.tender_id, self.cancellation_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, 'content3')

        self.set_status('complete')

        response = self.app.put('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(
            self.tender_id, self.cancellation_id, doc_id, self.tender_token), upload_files=[('file', 'name.doc', 'content3')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (complete) tender status")

    def test_patch_tender_cancellation_document(self):
        response = self.app.post('/tenders/{}/cancellations/{}/documents?acc_token={}'.format(
            self.tender_id, self.cancellation_id, self.tender_token), upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.patch_json('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(self.tender_id, self.cancellation_id, doc_id, self.tender_token), {"data": {"description": "document description"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])

        response = self.app.get('/tenders/{}/cancellations/{}/documents/{}'.format(
            self.tender_id, self.cancellation_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('document description', response.json["data"]["description"])

        self.set_status('complete')

        response = self.app.patch_json('/tenders/{}/cancellations/{}/documents/{}?acc_token={}'.format(self.tender_id, self.cancellation_id, doc_id, self.tender_token), {"data": {"description": "document description"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (complete) tender status")

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CompetitiveDialogUACancellationResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogUALotsCancellationResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogUALotCancellationResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogEUCancellationResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogEULotCancellationResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogEULotsCancellationResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
