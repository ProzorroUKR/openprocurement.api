# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy
from datetime import timedelta

from openprocurement.api.models import get_now
from openprocurement.api.tests.base import test_organization
from openprocurement.tender.competitivedialogue.tests.base import (BaseCompetitiveDialogUAContentWebTest,
                                                                   BaseCompetitiveDialogEUContentWebTest,
                                                                   test_tender_data_eu as test_tender_data,
                                                                   test_tender_data_ua,
                                                                   test_lots,
                                                                   test_bids_cd as test_bids)

from openprocurement.tender.competitivedialogue.models import FEATURES_MAX_SUM


class CompetitiveDialogueEULotResourceTest(BaseCompetitiveDialogEUContentWebTest):

    initial_auth = ('Basic', ('broker', ''))

    def test_create_tender_lot_invalid(self):
        response = self.app.post_json('/tenders/some_id/lots', {'data': {'title': 'lot title',
                                                                         'description': 'lot description'}},
                                      status=404)
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
            {u'description': u"Content-Type header should be one of ['application/json']",
             u'location': u'header',
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

        response = self.app.post_json(request_path, {'data': {}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'minimalStep'},
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'value'},
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

        response = self.app.post_json(request_path, {'data': {'value': 'invalid_value'}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'Please use a mapping for this field or Value instance instead of unicode.'],
             u'location': u'body',
             u'name': u'value'}
        ])

        response = self.app.post_json(request_path, {'data': {
            'title': 'lot title',
            'description': 'lot description',
            'value': {'amount': '100.0'},
            'minimalStep': {'amount': '500.0'},
        }}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'value should be less than value of lot'], u'location': u'body', u'name': u'minimalStep'}
        ])

        response = self.app.post_json(request_path, {'data': {
            'title': 'lot title',
            'description': 'lot description',
            'value': {'amount': '500.0'},
            'minimalStep': {'amount': '100.0', 'currency': "USD"}
        }})
        self.assertEqual(response.status, '201 Created')
        # but minimalStep currency stays unchanged
        response = self.app.get(request_path)
        self.assertEqual(response.content_type, 'application/json')
        lots = response.json['data']
        self.assertEqual(len(lots), 1)
        self.assertEqual(lots[0]['minimalStep']['currency'], "UAH")
        self.assertEqual(lots[0]['minimalStep']['amount'], 100)

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"items": [{'relatedLot': '0' * 32}]}},
                                       status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'relatedLot': [u'relatedLot should be one of lots']}],
             u'location': u'body',
             u'name': u'items'}
        ])

    def test_create_tender_lot(self):
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertEqual(lot['title'], 'lot title')
        self.assertEqual(lot['description'], 'lot description')
        self.assertIn('id', lot)
        self.assertIn(lot['id'], response.headers['Location'])
        self.assertNotIn('guarantee', lot)

        lot2 = deepcopy(test_lots[0])
        lot2['guarantee'] = {"amount": 100500, "currency": "USD"}
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': lot2})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        data = response.json['data']
        self.assertIn('guarantee', data)
        self.assertEqual(data['guarantee']['amount'], 100500)
        self.assertEqual(data['guarantee']['currency'], "USD")

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 100500)
        self.assertEqual(response.json['data']['guarantee']['currency'], "USD")
        self.assertNotIn('guarantee', response.json['data']['lots'][0])

        lot3 = deepcopy(test_lots[0])
        lot3['guarantee'] = {"amount": 500, "currency": "UAH"}
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': lot3},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'lot guarantee currency should be identical to tender guarantee currency'],
             u'location': u'body',
             u'name': u'lots'}
        ])

        lot3['guarantee'] = {"amount": 500}
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': lot3},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'lot guarantee currency should be identical to tender guarantee currency'], u'location': u'body', u'name': u'lots'}
        ])

        lot3['guarantee'] = {"amount": 20, "currency": "USD"}
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': lot3})
        self.assertEqual(response.status, '201 Created')
        data = response.json['data']
        self.assertIn('guarantee', data)
        self.assertEqual(data['guarantee']['amount'], 20)
        self.assertEqual(data['guarantee']['currency'], "USD")

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 100500 + 20)
        self.assertEqual(response.json['data']['guarantee']['currency'], "USD")

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"guarantee": {"currency": "EUR"}}})
        self.assertEqual(response.json['data']['guarantee']['amount'], 100500 + 20)
        self.assertEqual(response.json['data']['guarantee']['currency'], "EUR")
        self.assertNotIn('guarantee', response.json['data']['lots'][0])
        self.assertEqual(response.json['data']['lots'][1]['guarantee']['amount'], 100500)
        self.assertEqual(response.json['data']['lots'][1]['guarantee']['currency'], "EUR")
        self.assertEqual(response.json['data']['lots'][2]['guarantee']['amount'], 20)
        self.assertEqual(response.json['data']['lots'][2]['guarantee']['currency'], "EUR")
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': lot}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'Lot id should be uniq for all lots'], u'location': u'body', u'name': u'lots'}
        ])

    def test_patch_tender_lot(self):
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']

        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'],
                                                                                 self.tender_token),
                                       {"data": {"title": "new title"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["title"], "new title")

        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                                 lot['id'],
                                                                                 self.tender_token),
                                       {"data": {"guarantee": {"amount": 12}}})
        self.assertEqual(response.status, '200 OK')
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 12)
        self.assertEqual(response.json['data']['guarantee']['currency'], 'UAH')

        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                                 lot['id'],
                                                                                 self.tender_token),
                                       {"data": {"guarantee": {"currency": "USD"}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['guarantee']['currency'], 'UAH')

        response = self.app.patch_json('/tenders/{}/lots/some_id'.format(self.tender_id),
                                       {"data": {"title": "other title"}},
                                       status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'lot_id'}
        ])

        response = self.app.patch_json('/tenders/some_id/lots/some_id',
                                       {"data": {"title": "other title"}},
                                       status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["title"], "new title")

        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'],
                                                                                 self.tender_token),
                                       {"data": {"title": "other title"}}, status=403)

        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't update lot in current (unsuccessful) tender status")

    def test_patch_tender_currency(self):
        # create lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertEqual(lot['value']['currency'], "UAH")

        # update tender currency without mimimalStep currency change
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"value": {"currency": "GBP"}}}, status=422)

        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'currency should be identical to currency of value of tender'],
             u'location': u'body', u'name': u'minimalStep'}
        ])

        # update tender currency
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"value": {"currency": "GBP"},
                                                 "minimalStep": {"currency": "GBP"}}
                                        })

        self.assertEqual(response.status, '200 OK')
        # log currency is updated too
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertEqual(lot['value']['currency'], "GBP")

        # try to update lot currency
        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                                 lot['id'],
                                                                                 self.tender_token),
                                       {"data": {"value": {"currency": "USD"}}})
        self.assertEqual(response.status, '200 OK')
        # but the value stays unchanged
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertEqual(lot['value']['currency'], "GBP")

        # try to update minimalStep currency
        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                                 lot['id'],
                                                                                 self.tender_token),
                                       {"data": {"minimalStep": {"currency": "USD"}}})
        self.assertEqual(response.status, '200 OK')
        # but the value stays unchanged
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertEqual(lot['minimalStep']['currency'], "GBP")

        # try to update lot minimalStep currency and lot value currency in single request
        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                                 lot['id'],
                                                                                 self.tender_token),
                                       {"data": {"value": {"currency": "USD"},
                                                 "minimalStep": {"currency": "USD"}}})
        self.assertEqual(response.status, '200 OK')
        # but the value stays unchanged
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertEqual(lot['value']['currency'], "GBP")
        self.assertEqual(lot['minimalStep']['currency'], "GBP")

    def test_patch_tender_vat(self):
        # set tender VAT
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"value": {"valueAddedTaxIncluded": True}}})

        self.assertEqual(response.status, '200 OK')

        # create lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertTrue(lot['value']['valueAddedTaxIncluded'])

        # update tender VAT
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"value": {"valueAddedTaxIncluded": False},
                                                 "minimalStep": {"valueAddedTaxIncluded": False}}})

        self.assertEqual(response.status, '200 OK')
        # log VAT is updated too
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertFalse(lot['value']['valueAddedTaxIncluded'])

        # try to update lot VAT
        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                                 lot['id'],
                                                                                 self.tender_token),
                                       {"data": {"value": {"valueAddedTaxIncluded": True}}})
        self.assertEqual(response.status, '200 OK')
        # but the value stays unchanged
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertFalse(lot['value']['valueAddedTaxIncluded'])

        # try to update minimalStep VAT
        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                                 lot['id'],
                                                                                 self.tender_token),
                                       {"data": {"minimalStep": {"valueAddedTaxIncluded": True}}})
        self.assertEqual(response.status, '200 OK')
        # but the value stays unchanged
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertFalse(lot['minimalStep']['valueAddedTaxIncluded'])

        # try to update minimalStep VAT and value VAT in single request
        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                                 lot['id'],
                                                                                 self.tender_token),
                                       {"data": {"value": {"valueAddedTaxIncluded": True},
                                                 "minimalStep": {"valueAddedTaxIncluded": True}}})
        self.assertEqual(response.status, '200 OK')
        # but the value stays unchanged
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertFalse(lot['value']['valueAddedTaxIncluded'])
        self.assertEqual(lot['minimalStep']['valueAddedTaxIncluded'], lot['value']['valueAddedTaxIncluded'])

    def test_get_tender_lot(self):
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']

        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(set(response.json['data']), set([u'id', u'title', u'date', u'description',
                                                          u'value', u'status', u'minimalStep']))

        self.set_status('active.qualification')

        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
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

    def test_get_tender_lots(self):
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']

        response = self.app.get('/tenders/{}/lots'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'title', u'date', u'description',
                                                             u'value', u'status', u'minimalStep']))

        self.set_status('active.qualification')

        response = self.app.get('/tenders/{}/lots'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'][0], lot)

        response = self.app.get('/tenders/some_id/lots', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

    def test_delete_tender_lot(self):
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']

        response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'],
                                                                             self.tender_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], lot)

        response = self.app.delete('/tenders/{}/lots/some_id?acc_token={}'.format(self.tender_id, self.tender_token),
                                   status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'lot_id'}
        ])

        response = self.app.delete('/tenders/some_id/lots/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"items": [{'relatedLot': lot['id']}]}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'],
                                                                             self.tender_token),
                                   status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'relatedLot': [u'relatedLot should be one of lots']}],
             u'location': u'body',
             u'name': u'items'}
        ])
        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'],
                                                                             self.tender_token),
                                   status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't delete lot in current (unsuccessful) tender status")

    def test_tender_lot_guarantee(self):
        data = deepcopy(test_tender_data)
        data['guarantee'] = {"amount": 100, "currency": "USD"}
        response = self.app.post_json('/tenders', {'data': data})
        tender = response.json['data']
        owner_token = response.json['access']['token']
        self.assertEqual(response.status, '201 Created')
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 100)
        self.assertEqual(response.json['data']['guarantee']['currency'], "USD")

        lot = deepcopy(test_lots[0])
        lot['guarantee'] = {"amount": 20, "currency": "USD"}
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender['id'], owner_token), {'data': lot})
        self.assertEqual(response.status, '201 Created')
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 20)
        self.assertEqual(response.json['data']['guarantee']['currency'], "USD")

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                       {'data': {'guarantee': {"currency": "GBP"}}})
        self.assertEqual(response.status, '200 OK')
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 20)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        lot['guarantee'] = {"amount": 20, "currency": "GBP"}
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender['id'], owner_token), {'data': lot})
        self.assertEqual(response.status, '201 Created')
        lot_id = response.json['data']['id']
        self.assertEqual(response.json['data']['guarantee']['amount'], 20)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        response = self.app.get('/tenders/{}'.format(tender['id']))
        self.assertEqual(response.json['data']['guarantee']['amount'], 20 + 20)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        lot2 = deepcopy(test_lots[0])
        lot2['guarantee'] = {"amount": 30, "currency": "GBP"}
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender['id'], owner_token), {'data': lot2})
        self.assertEqual(response.status, '201 Created')
        lot2_id = response.json['data']['id']
        self.assertEqual(response.json['data']['guarantee']['amount'], 30)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        lot2['guarantee'] = {"amount": 40, "currency": "USD"}
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender['id'], owner_token), {'data': lot2},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'lot guarantee currency should be identical to tender guarantee currency'],
             u'location': u'body',
             u'name': u'lots'}
        ])

        response = self.app.get('/tenders/{}'.format(tender['id']))
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 20 + 20 + 30)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                       {"data": {"guarantee": {"amount": 55}}})
        self.assertEqual(response.json['data']['guarantee']['amount'], 20 + 20 + 30)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(tender['id'], lot2_id, owner_token),
                                       {'data': {'guarantee': {"amount": 35, "currency": "GBP"}}})
        self.assertEqual(response.json['data']['guarantee']['amount'], 35)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        response = self.app.get('/tenders/{}'.format(tender['id']))
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 20 + 20 + 35)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        for l_id in (lot_id, lot2_id):
            response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(tender['id'], l_id, owner_token),
                                           {'data': {'guarantee': {"amount": 0, "currency": "GBP"}}})
            self.assertEqual(response.json['data']['guarantee']['amount'], 0)
            self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        response = self.app.get('/tenders/{}'.format(tender['id']))
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 20)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        for l_id in (lot_id, lot2_id):
            response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(tender['id'], l_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        response = self.app.get('/tenders/{}'.format(tender['id']))
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 20)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")


class CompetitiveDialogueEULotEdgeCasesTest(BaseCompetitiveDialogEUContentWebTest):
    initial_auth = ('Basic', ('broker', ''))
    initial_lots = test_lots * 2

    def setUp(self):
        uniq_bids = [deepcopy(bid) for bid in test_bids]
        for n, bid in enumerate(uniq_bids):
            bid['tenderers'][0]['identifier']['id'] = '00000{}'.format(n)
        self.initial_bids = uniq_bids
        super(CompetitiveDialogueEULotEdgeCasesTest, self).setUp()

    def test_question_blocking(self):
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'lot',
                                                'relatedItem': self.initial_lots[0]['id'],
                                                'author': test_organization}})
        question = response.json['data']
        self.assertEqual(question['questionOf'], 'lot')
        self.assertEqual(question['relatedItem'], self.initial_lots[0]['id'])

        self.set_status('active.pre-qualification', extra={"status": "active.tendering"})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], 'active.tendering')

        # cancel lot
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'active',
                                                "cancellationOf": "lot",
                                                "relatedLot": self.initial_lots[0]['id']}})

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

    def test_claim_blocking(self):
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id),
                                      {'data': {'title': 'complaint title',
                                                'description': 'complaint description',
                                                'author': test_organization,
                                                'relatedLot': self.initial_lots[0]['id'],
                                                'status': 'claim'}})
        self.assertEqual(response.status, '201 Created')
        complaint = response.json['data']
        self.assertEqual(complaint['relatedLot'], self.initial_lots[0]['id'])

        self.set_status('active.pre-qualification', extra={"status": "active.tendering"})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], 'active.tendering')

        # cancel lot
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'active',
                                                "cancellationOf": "lot",
                                                "relatedLot": self.initial_lots[0]['id']}})

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

    def test_next_check_value_with_unanswered_question(self):
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'lot',
                                                'relatedItem': self.initial_lots[0]['id'],
                                                'author': test_organization}})
        question = response.json['data']
        self.assertEqual(question['questionOf'], 'lot')
        self.assertEqual(question['relatedItem'], self.initial_lots[0]['id'])

        self.set_status('active.pre-qualification', extra={"status": "active.tendering"})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], 'active.tendering')
        self.assertNotIn('next_check', response.json['data'])

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'active',
                                                "cancellationOf": "lot",
                                                "relatedLot": self.initial_lots[0]['id']}})

        response = self.app.get('/tenders/{}'.format(self.tender_id, ))
        self.assertIn('next_check', response.json['data'])
        self.assertEqual(response.json['data']['next_check'], response.json['data']['tenderPeriod']['endDate'])

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], 'active.pre-qualification')

    def test_next_check_value_with_unanswered_claim(self):
        response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id),
                                      {'data': {'title': 'complaint title',
                                                'description': 'complaint description',
                                                'author': test_organization,
                                                'relatedLot': self.initial_lots[0]['id'],
                                                'status': 'claim'}})
        self.assertEqual(response.status, '201 Created')
        complaint = response.json['data']
        self.assertEqual(complaint['relatedLot'], self.initial_lots[0]['id'])

        self.set_status('active.pre-qualification', extra={"status": "active.tendering"})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], 'active.tendering')
        self.assertNotIn('next_check', response.json['data'])

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'active',
                                                "cancellationOf": "lot",
                                                "relatedLot": self.initial_lots[0]['id']}})

        response = self.app.get('/tenders/{}'.format(self.tender_id, ))
        self.assertIn('next_check', response.json['data'])
        self.assertEqual(response.json['data']['next_check'], response.json['data']['tenderPeriod']['endDate'])

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], 'active.pre-qualification')


class CompetitiveDialogueEULotFeatureResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_lots = 2 * test_lots
    initial_auth = ('Basic', ('broker', ''))

    def test_tender_value(self):
        request_path = '/tenders/{}'.format(self.tender_id)
        response = self.app.get(request_path)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['value']['amount'], sum([i['value']['amount'] for i in self.initial_lots]))

    def test_tender_features_invalid(self):
        request_path = '/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token)
        data = test_tender_data.copy()
        item = data['items'][0].copy()
        item['id'] = "1"
        data['items'] = [item]
        data['features'] = [
            {
                "featureOf": "lot",
                "relatedItem": self.initial_lots[0]['id'],
                "title": u"Потужність всмоктування",
                "enum": [
                    {
                        "value": 1.0,
                        "title": u"До 1000 Вт"
                    },
                    {
                        "value": 0.15,
                        "title": u"Більше 1000 Вт"
                    }
                ]
            }
        ]
        response = self.app.patch_json(request_path, {'data': data}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'enum': [{u'value': [u'Float value should be less than 0.99.']}]}],
             u'location': u'body',
             u'name': u'features'}
        ])
        data['features'][0]["enum"][0]["value"] = 0.3
        data['features'].append(data['features'][0].copy())
        data['features'][1]["enum"][0]["value"] = 0.3
        data['features'].append(data['features'][0].copy())
        data['features'][2]["enum"][0]["value"] = 0.3
        data['features'].append(data['features'][0].copy())
        data['features'][3]["enum"][0]["value"] = 0.3
        response = self.app.patch_json(request_path, {'data': data}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'Sum of max value of all features for lot should be less then or equal to {:.0f}%'.format(FEATURES_MAX_SUM * 100)],
             u'location': u'body',
             u'name': u'features'}
        ])
        data['features'][1]["enum"][0]["value"] = 0.1
        data['features'].append(data['features'][0].copy())
        data['features'][2]["relatedItem"] = self.initial_lots[1]['id']
        data['features'].append(data['features'][2].copy())
        response = self.app.patch_json(request_path, {'data': data})
        self.assertEqual(response.status, '200 OK')


class CompetitiveDialogueEULotBidderResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_lots = test_lots
    initial_auth = ('Basic', ('broker', ''))

    def test_create_tender_bidder_invalid(self):
        request_path = '/tenders/{}/bids'.format(self.tender_id)
        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers']}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'lotValues'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers'],
                                                              'lotValues': [{"value": {"amount": 500}}]}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'relatedLot': [u'This field is required.']}],
             u'location': u'body',
             u'name': u'lotValues'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers'],
                                                              'lotValues': [{"value": {"amount": 500},
                                                                             'relatedLot': "0" * 32}]}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'relatedLot': [u'relatedLot should be one of lots']}], u'location': u'body', u'name': u'lotValues'}
        ])

        # Field 'value' doesn't exists on first stage
        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers'],
                                                              'lotValues': [{"value": {"amount": 5000000},
                                                                             'relatedLot': self.initial_lots[0]['id']}]}
                                                     })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers'],
                                                              'lotValues': [{"value": {"amount": 500,
                                                                                       'valueAddedTaxIncluded': False},
                                                                             'relatedLot': self.initial_lots[0]['id']}]}
                                                     })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers'],
                                                              'lotValues': [{"value": {"amount": 500,
                                                                                       'currency': "USD"},
                                                                             'relatedLot': self.initial_lots[0]['id']}]}
                                                     })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers'],
                                                              "value": {"amount": 500},
                                                              'lotValues': [{"value": {"amount": 500},
                                                                             'relatedLot': self.initial_lots[0]['id']}]}
                                                     })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

    def test_patch_tender_bidder(self):
        lot_id = self.initial_lots[0]['id']
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True,
                                                'selfQualified': True,
                                                'tenderers': test_bids[0]["tenderers"],
                                                'lotValues': [{"value": {"amount": 500},
                                                               'relatedLot': lot_id}]}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bidder = response.json['data']
        bid_token = response.json['access']['token']
        lot = bidder['lotValues'][0]

        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bidder['id'], bid_token),
                                       {"data": {'tenderers': [{"name": u"Державне управління управлінням справами"}]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lotValues'][0]['date'], lot['date'])
        self.assertNotEqual(response.json['data']['tenderers'][0]['name'], bidder['tenderers'][0]['name'])

        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bidder['id'], bid_token),
                                       {"data": {'lotValues': [{"value": {"amount": 500},
                                                                'relatedLot': lot_id}],
                                                 'tenderers': test_bids[0]["tenderers"]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lotValues'][0]['date'], lot['date'])
        self.assertEqual(response.json['data']['tenderers'][0]['name'], bidder['tenderers'][0]['name'])

        # If we don't change anything then return null
        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bidder['id'], bid_token),
                                       {"data": {'lotValues': [{"value": {"amount": 400}, 'relatedLot': lot_id}]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bidder['id'], bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertNotIn('lotValues', response.json['data'])

        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bidder['id'], bid_token),
                                       {"data": {'lotValues': [{"value": {"amount": 500},
                                                                'relatedLot': lot_id}],
                                                 'status': 'active'}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update bid in current (unsuccessful) tender status")


class CompetitiveDialogueEULotFeatureBidderResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_lots = test_lots
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(CompetitiveDialogueEULotFeatureBidderResourceTest, self).setUp()
        self.lot_id = self.initial_lots[0]['id']
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token), {"data": {
            "items": [
                {
                    'relatedLot': self.lot_id,
                    'id': '1'
                }
            ],
            "features": [
                {
                    "code": "code_item",
                    "featureOf": "item",
                    "relatedItem": "1",
                    "title": u"item feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                },
                {
                    "code": "code_lot",
                    "featureOf": "lot",
                    "relatedItem": self.lot_id,
                    "title": u"lot feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                },
                {
                    "code": "code_tenderer",
                    "featureOf": "tenderer",
                    "title": u"tenderer feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                }
            ]
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['items'][0]['relatedLot'], self.lot_id)

    def test_create_tender_bidder_invalid(self):
        request_path = '/tenders/{}/bids'.format(self.tender_id)
        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers']}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers'],
                                                              'lotValues': [{"value": {"amount": 500}}]}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'relatedLot': [u'This field is required.']}], u'location': u'body', u'name': u'lotValues'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers'],
                                                              'lotValues': [{"value": {"amount": 500},
                                                                             'relatedLot': "0" * 32}]}},
                                    status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'relatedLot': [u'relatedLot should be one of lots']}],
             u'location': u'body',
             u'name': u'lotValues'}
        ])

        # Field 'value' doesn't exists on first stage
        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers'],
                                                              'lotValues': [{"value": {"amount": 5000000},
                                                                             'relatedLot': self.lot_id}]}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers'],
                                                              'lotValues': [{"value": {"amount": 500,
                                                                                       'valueAddedTaxIncluded': False},
                                                                             'relatedLot': self.lot_id}]}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers'],
                                                              'lotValues': [{"value": {"amount": 500,
                                                                                       'currency': "USD"},
                                                                             'relatedLot': self.lot_id}]}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

    def test_create_tender_bidder(self):
        request_path = '/tenders/{}/bids'.format(self.tender_id)
        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]["tenderers"],
                                                              'lotValues': [{"value": {"amount": 500},
                                                                             'relatedLot': self.lot_id}],
                                                              'parameters': [{"code": "code_item", "value": 0.01},
                                                                             {"code": "code_tenderer", "value": 0.01},
                                                                             {"code": "code_lot", "value": 0.01}]}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bidder = response.json['data']
        self.assertEqual(bidder['tenderers'][0]['name'], test_tender_data["procuringEntity"]['name'])
        self.assertIn('id', bidder)
        self.assertIn(bidder['id'], response.headers['Location'])

        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]["tenderers"],
                                                              'lotValues': [{"value": {"amount": 500},
                                                                             'relatedLot': self.lot_id}],
                                                              'parameters': [{"code": "code_item", "value": 0.01},
                                                                             {"code": "code_tenderer", "value": 0.01},
                                                                             {"code": "code_lot", "value": 0.01}]}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add bid in current (unsuccessful) tender status")


class CompetitiveDialogueEULotProcessTest(BaseCompetitiveDialogEUContentWebTest):

    def test_1lot_0bid(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # create tender
        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        # add lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                      {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        lot_id = response.json['data']['id']
        # add relatedLot for item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [{'relatedLot': lot_id}]}})
        self.assertEqual(response.status, '200 OK')
        # switch to active.tendering
        response = self.set_status('active.tendering')
        self.assertNotIn("auctionPeriod", response.json['data']['lots'][0])
        # switch to unsuccessful
        response = self.set_status('active.stage2.pending', {'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
        self.assertEqual(response.json['data']["lots"][0]['status'], 'unsuccessful')
        self.assertEqual(response.json['data']['status'], 'unsuccessful')

        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                      {'data': test_lots[0]},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [{
            "location": "body", "name": "data", "description": "Can't add lot in current (unsuccessful) tender status"
        }])

    def test_1lot_1bid(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # create tender
        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        # add lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                      {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        lot_id = response.json['data']['id']
        # add relatedLot for item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [{'relatedLot': lot_id}]}})
        self.assertEqual(response.status, '200 OK')
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True,
                                                'selfQualified': True,
                                                'tenderers': test_bids[0]["tenderers"],
                                                'lotValues': [{"value": {"amount": 500},
                                                               'relatedLot': lot_id}]}})
        # switch to active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.check_chronograph()
        # switch to unsuccessful
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}?acc_token={}'.format(tender_id, owner_token))
        self.assertEqual(response.json['data']['status'], 'unsuccessful')

    def test_1lot_2bid_1unqualified(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # create tender
        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        # add lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                      {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        lot_id = response.json['data']['id']
        # add relatedLot for item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [{'relatedLot': lot_id}]}})
        self.assertEqual(response.status, '200 OK')
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        bidder_data = deepcopy(test_bids[0]['tenderers'][0])
        bidder_data['identifier']['id'] = u"00037256"
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True,
                                                'selfQualified': True,
                                                'tenderers': [bidder_data],
                                                'lotValues': [{"value": {"amount": 500},
                                                               'relatedLot': lot_id}]}})

        bidder_data['identifier']['id'] = u"00037257"
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True,
                                                'selfQualified': True,
                                                'tenderers': [bidder_data],
                                                'lotValues': [{"value": {"amount": 500},
                                                               'relatedLot': lot_id}]}})
        bidder_data['identifier']['id'] = u"00037258"
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True,
                                                'selfQualified': True,
                                                'tenderers': [bidder_data],
                                                'lotValues': [{"value": {"amount": 500},
                                                               'relatedLot': lot_id}]}})
        # switch to active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']

        response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                           qualifications[0]['id'],
                                                                                           owner_token),
                                       {"data": {'status': 'active', "qualified": True, "eligible": True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active')

        response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                           qualifications[1]['id'],
                                                                                           owner_token),
                                       {"data": {'status': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'unsuccessful')
        response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                           qualifications[2]['id'],
                                                                                           owner_token),
                                       {"data": {'status': 'active', "qualified": True, "eligible": True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active')
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "active.pre-qualification.stand-still")

    def test_1lot_2bid(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # create tender
        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        # add lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                      {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        lot_id = response.json['data']['id']
        self.initial_lots = [response.json['data']]
        # add relatedLot for item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [{'relatedLot': lot_id}]}})
        self.assertEqual(response.status, '200 OK')
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        bidder_data = deepcopy(test_bids[0]['tenderers'][0])
        bidder_data['identifier']['id'] = u"00037256"
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True,
                                                'selfQualified': True,
                                                'tenderers': [bidder_data],
                                                'lotValues': [{"value": {"amount": 450},
                                                               'relatedLot': lot_id}]}})
        bid_id = response.json['data']['id']
        bid_token = response.json['access']['token']
        # create second bid
        self.app.authorization = ('Basic', ('broker', ''))
        bidder_data['identifier']['id'] = u"00037257"
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True,
                                                'selfQualified': True,
                                                'tenderers': [bidder_data],
                                                'lotValues': [{"value": {"amount": 475},
                                                               'relatedLot': lot_id}]}})
        # create third
        bidder_data['identifier']['id'] = u"00037258"
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True,
                                                'selfQualified': True,
                                                'tenderers': [bidder_data],
                                                'lotValues': [{"value": {"amount": 470},
                                                               'relatedLot': lot_id}]}})
        # switch to active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']
        for qualification in qualifications:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                               qualification['id'],
                                                                                               owner_token),
                                      {"data": {'status': 'active', "qualified": True, "eligible": True}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active')

        response = self.app.get('/tenders/{}?acc_token={}'.format(tender_id, owner_token))
        self.assertEqual(response.status, '200 OK')

        for bid in response.json['data']['bids']:
            self.assertEqual(bid['status'], 'active')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")
        self.check_chronograph()

        response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token))
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.status, "200 OK")

    def test_2lot_2bid_1lot_del(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # create tender
        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        lots = []
        for lot in 2 * test_lots:
            # add lot
            response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                          {'data': test_lots[0]})
            self.assertEqual(response.status, '201 Created')
            lots.append(response.json['data']['id'])
        self.initial_lots = lots
        # add item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [test_tender_data['items'][0] for i in lots]}})

        response = self.set_status('active.tendering')
        # create bid

        bids = []
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True,
                                                'selfQualified': True,
                                                'tenderers': test_bids[0]["tenderers"],
                                                'lotValues': [{"value": {"amount": 500}, 'relatedLot': lot_id}
                                                              for lot_id in lots
                                                              ]}})
        bids.append(response.json)
        # create second bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                                'tenderers': test_bids[1]["tenderers"],
                                                'lotValues': [{"value": {"amount": 500}, 'relatedLot': lot_id}
                                                              for lot_id in lots
                                                              ]}})
        bids.append(response.json)
        response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lots[0], owner_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

    def test_1lot_3bid_1del(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # create tender
        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        # add lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                      {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        lot_id = response.json['data']['id']
        self.initial_lots = [response.json['data']]
        # add relatedLot for item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [{'relatedLot': lot_id}]}})
        self.assertEqual(response.status, '200 OK')
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        bids = []
        self.assertEqual(len(test_bids), 3)
        bidder_data = deepcopy(test_bids[0]['tenderers'][0])
        for index, test_bid in enumerate(test_bids):
            bidder_data['identifier']['id'] = str(00037256+index)
            response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                          {'data': {'selfEligible': True,
                                                    'selfQualified': True,
                                                    'tenderers': [bidder_data],
                                                    'lotValues': [{"value": {"amount": 450},
                                                                   'relatedLot': lot_id}]}})
            bids.append({response.json['data']['id']: response.json['access']['token']})

        response = self.app.delete('/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bids[2].keys()[0],
                                                                             bids[2].values()[0]))
        self.assertEqual(response.status, '200 OK')

        # try switch to active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.get('/tenders/{}?acc_token={}'.format(tender_id, owner_token))
        self.assertTrue(all([i['status'] == 'unsuccessful' for i in response.json['data']['lots']]))
        self.assertEqual(response.json['data']['status'], 'unsuccessful')

    def test_1lot_3bid_1un(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # create tender
        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        # add lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token), {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        lot_id = response.json['data']['id']
        self.initial_lots = [response.json['data']]
        # add relatedLot for item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [{'relatedLot': lot_id}]}})
        self.assertEqual(response.status, '200 OK')
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        bids = []
        bidder_data = deepcopy(test_bids[0]['tenderers'][0])
        for i in range(3):
            bidder_data['identifier']['id'] = str(00037256 + i)
            response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                          {'data': {'selfEligible': True, 'selfQualified': True,
                                                    'tenderers': [bidder_data],
                                                    'lotValues': [{"value": {"amount": 450},
                                                                   'relatedLot': lot_id}]}})
            bids.append({response.json['data']['id']: response.json['access']['token']})

        # switch to active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']
        for qualification in qualifications:
            if qualification['bidID'] == bids[2].keys()[0]:
                response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                                   qualification['id'],
                                                                                                   owner_token),
                                          {"data": {'status': 'unsuccessful'}})
                self.assertEqual(response.status, '200 OK')
                self.assertEqual(response.json['data']['status'], 'unsuccessful')
            else:
                response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                                   qualification['id'],
                                                                                                   owner_token),
                                          {"data": {'status': 'active', "qualified": True, "eligible": True}})
                self.assertEqual(response.status, '200 OK')
                self.assertEqual(response.json['data']['status'], 'active')
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")
        self.check_chronograph()

        response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token))
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.status, "200 OK")

        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']

    def test_2lot_0bid(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # create tender
        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        lots = []
        for lot in 2 * test_lots:
            # add lot
            response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                          {'data': test_lots[0]})
            self.assertEqual(response.status, '201 Created')
            lots.append(response.json['data']['id'])
        # add item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [test_tender_data['items'][0] for i in lots]}})
        # add relatedLot for item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [{'relatedLot': i} for i in lots]}})
        self.assertEqual(response.status, '200 OK')

        self.time_shift('active.pre-qualification')
        self.check_chronograph()
        # switch to unsuccessful
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}?acc_token={}'.format(tender_id, owner_token))
        self.assertTrue(all([i['status'] == 'unsuccessful' for i in response.json['data']['lots']]))
        self.assertEqual(response.json['data']['status'], 'unsuccessful')

    def test_2lot_2can(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # create tender
        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        lots = []
        for lot in 2 * test_lots:
            # add lot
            response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                          {'data': test_lots[0]})
            self.assertEqual(response.status, '201 Created')
            lots.append(response.json['data']['id'])
        # add item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [test_tender_data['items'][0] for i in lots]}})
        # add relatedLot for item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [{'relatedLot': i} for i in lots]}})
        self.assertEqual(response.status, '200 OK')
        # cancel every lot
        for lot_id in lots:
            response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(tender_id, owner_token),
                                          {'data': {'reason': 'cancellation reason',
                                                    'status': 'active',
                                                    "cancellationOf": "lot",
                                                    "relatedLot": lot_id}})
        response = self.app.get('/tenders/{}'.format(tender_id))
        self.assertTrue(all([i['status'] == 'cancelled' for i in response.json['data']['lots']]))
        self.assertEqual(response.json['data']['status'], 'cancelled')

    def test_2lot_1can(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # create tender
        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        lots = []
        for lot in 2 * test_lots:
            # add lot
            response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                          {'data': test_lots[0]})
            self.assertEqual(response.status, '201 Created')
            lots.append(response.json['data']['id'])
        # add item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [test_tender_data['items'][0] for i in lots]}})
        # add relatedLot for item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [{'relatedLot': i} for i in lots]}})
        self.assertEqual(response.status, '200 OK')
        # cancel first lot
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(tender_id, owner_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'active',
                                                "cancellationOf": "lot",
                                                "relatedLot": lots[0]}})

        response = self.app.get('/tenders/{}'.format(tender_id))
        self.assertFalse(all([i['status'] == 'cancelled' for i in response.json['data']['lots']]))
        self.assertTrue(any([i['status'] == 'cancelled' for i in response.json['data']['lots']]))
        self.assertEqual(response.json['data']['status'], 'active.tendering')

        # try to restore lot back by old cancellation
        response = self.app.get('/tenders/{}/cancellations?acc_token={}'.format(tender_id, owner_token))
        self.assertEqual(len(response.json['data']), 1)
        cancellation = response.json['data'][0]
        self.assertEqual(cancellation['status'], 'active')

        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(tender_id, cancellation['id'],
                                                                                          owner_token),
                                      {'data': {'status': 'pending'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'][0]["description"], "Can update cancellation only in active lot status")

        # try to restore lot back by new pending cancellation
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(tender_id, owner_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'pending',
                                                "cancellationOf": "lot",
                                                "relatedLot": lots[0]}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'][0]["description"], "Can add cancellation only in active lot status")
        response = self.app.get('/tenders/{}'.format(tender_id))
        self.assertFalse(all([i['status'] == 'cancelled' for i in response.json['data']['lots']]))
        self.assertTrue(any([i['status'] == 'cancelled' for i in response.json['data']['lots']]))
        self.assertEqual(response.json['data']['status'], 'active.tendering')

    def test_2lot_2bid_0com_1can(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # create tender
        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        lots = []
        for lot in 2 * test_lots:
            # add lot
            response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                          {'data': test_lots[0]})
            self.assertEqual(response.status, '201 Created')
            lots.append(response.json['data']['id'])
        # add item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [test_tender_data['items'][0] for i in lots]}})
        # add relatedLot for item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [{'relatedLot': i} for i in lots]}})
        self.assertEqual(response.status, '200 OK')
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        bidder_data = deepcopy(test_bids[0]['tenderers'][0])
        bidder_data['identifier']['id'] = u"00037256"
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True,
                                                'selfQualified': True,
                                                'tenderers': [bidder_data],
                                                'lotValues': [{"value": {"amount": 500}, 'relatedLot': lot_id}
                                                              for lot_id in lots]}})

        bidder_data['identifier']['id'] = u"00037257"
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True,
                                                'selfQualified': True,
                                                'tenderers': [bidder_data],
                                                'lotValues': [{"value": {"amount": 499}, 'relatedLot': lot_id}
                                                              for lot_id in lots]}})

        bidder_data['identifier']['id'] = u"00037258"
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True,
                                                'selfQualified': True,
                                                'tenderers': [bidder_data],
                                                'lotValues': [{"value": {"amount": 499}, 'relatedLot': lot_id}
                                                              for lot_id in lots]}})

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(tender_id, owner_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'active',
                                                "cancellationOf": "lot",
                                                "relatedLot": lots[0]}})
        response = self.app.get('/tenders/{}?acc_token={}'.format(tender_id, owner_token))
        self.assertEqual(response.status, "200 OK")
        # active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']
        self.assertEqual(len(qualifications), 3)

        for qualification in qualifications:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                               qualification['id'],
                                                                                               owner_token),
                                      {"data": {'status': 'active', "qualified": True, "eligible": True}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active')
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")


    def test_2lot_2bid_2com_2win(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # create tender
        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        lots = []
        for lot in 2 * test_lots:
            # add lot
            response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                          {'data': test_lots[0]})
            self.assertEqual(response.status, '201 Created')
            lots.append(response.json['data']['id'])
        self.initial_lots = lots
        # add item
        self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                            {"data": {"items": [test_tender_data['items'][0] for i in lots]}})
        # add relatedLot for item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [{'relatedLot': i} for i in lots]}})
        self.assertEqual(response.status, '200 OK')
        # create bid
        bidder_data = deepcopy(test_bids[0]['tenderers'][0])
        bidder_data['identifier']['id'] = u"00037256"
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.post_json('/tenders/{}/bids'.format(tender_id),
                           {'data': {'selfEligible': True,
                                     'selfQualified': True,
                                     'tenderers': [bidder_data],
                                     'lotValues': [{"value": {"amount": 500}, 'relatedLot': lot_id}
                                                   for lot_id in lots]}})
        # create second bid
        bidder_data['identifier']['id'] = u"00037257"
        self.app.post_json('/tenders/{}/bids'.format(tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                                                           'tenderers': [bidder_data],
                                                                           'lotValues': [{"value": {"amount": 500},
                                                                                          'relatedLot': lot_id}
                                                                                         for lot_id in lots]}})
        # create third bid
        bidder_data['identifier']['id'] = u"00037258"
        self.app.post_json('/tenders/{}/bids'.format(tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                                                           'tenderers': [bidder_data],
                                                                           'lotValues': [{"value": {"amount": 500},
                                                                                          'relatedLot': lot_id}
                                                                                         for lot_id in lots]}})
        # switch to active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.check_chronograph()
        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']
        self.assertEqual(len(qualifications), 6)

        for qualification in qualifications:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                               qualification['id'],
                                                                                               owner_token),
                                           {"data": {'status': 'active', "qualified": True, "eligible": True}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active')
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")


class CompetitiveDialogueUALotResourceTest(BaseCompetitiveDialogUAContentWebTest):

    initial_auth = ('Basic', ('broker', ''))

    def test_create_tender_lot_invalid(self):
        response = self.app.post_json('/tenders/some_id/lots', {'data': {'title': 'lot title',
                                                                         'description': 'lot description'}},
                                      status=404)
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
            {u'description': u"Content-Type header should be one of ['application/json']",
             u'location': u'header',
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

        response = self.app.post_json(request_path, {'data': {}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'minimalStep'},
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'value'},
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'title'}
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

        response = self.app.post_json(request_path, {'data': {'value': 'invalid_value'}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'Please use a mapping for this field or Value instance instead of unicode.'],
             u'location': u'body',
             u'name': u'value'}
        ])

        response = self.app.post_json(request_path, {'data': {
            'title': 'lot title',
            'description': 'lot description',
            'value': {'amount': '100.0'},
            'minimalStep': {'amount': '500.0'},
        }}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'value should be less than value of lot'], u'location': u'body', u'name': u'minimalStep'}
        ])

        response = self.app.post_json(request_path, {'data': {
            'title': 'lot title',
            'description': 'lot description',
            'value': {'amount': '500.0'},
            'minimalStep': {'amount': '100.0', 'currency': "USD"}
        }})
        self.assertEqual(response.status, '201 Created')
        # but minimalStep currency stays unchanged
        response = self.app.get(request_path)
        self.assertEqual(response.content_type, 'application/json')
        lots = response.json['data']
        self.assertEqual(len(lots), 1)
        self.assertEqual(lots[0]['minimalStep']['currency'], "UAH")
        self.assertEqual(lots[0]['minimalStep']['amount'], 100)

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"items": [{'relatedLot': '0' * 32}]}},
                                       status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'relatedLot': [u'relatedLot should be one of lots']}],
             u'location': u'body',
             u'name': u'items'}
        ])

    def test_create_tender_lot(self):
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertEqual(lot['title'], 'lot title')
        self.assertEqual(lot['description'], 'lot description')
        self.assertIn('id', lot)
        self.assertIn(lot['id'], response.headers['Location'])
        self.assertNotIn('guarantee', lot)

        lot2 = deepcopy(test_lots[0])
        lot2['guarantee'] = {"amount": 100500, "currency": "USD"}
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': lot2})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        data = response.json['data']
        self.assertIn('guarantee', data)
        self.assertEqual(data['guarantee']['amount'], 100500)
        self.assertEqual(data['guarantee']['currency'], "USD")

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 100500)
        self.assertEqual(response.json['data']['guarantee']['currency'], "USD")
        self.assertNotIn('guarantee', response.json['data']['lots'][0])

        lot3 = deepcopy(test_lots[0])
        lot3['guarantee'] = {"amount": 500, "currency": "UAH"}
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': lot3},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'lot guarantee currency should be identical to tender guarantee currency'],
             u'location': u'body',
             u'name': u'lots'}
        ])

        lot3['guarantee'] = {"amount": 500}
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': lot3},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'lot guarantee currency should be identical to tender guarantee currency'], u'location': u'body', u'name': u'lots'}
        ])

        lot3['guarantee'] = {"amount": 20, "currency": "USD"}
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': lot3})
        self.assertEqual(response.status, '201 Created')
        data = response.json['data']
        self.assertIn('guarantee', data)
        self.assertEqual(data['guarantee']['amount'], 20)
        self.assertEqual(data['guarantee']['currency'], "USD")

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 100500 + 20)
        self.assertEqual(response.json['data']['guarantee']['currency'], "USD")

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"guarantee": {"currency": "EUR"}}})
        self.assertEqual(response.json['data']['guarantee']['amount'], 100500 + 20)
        self.assertEqual(response.json['data']['guarantee']['currency'], "EUR")
        self.assertNotIn('guarantee', response.json['data']['lots'][0])
        self.assertEqual(response.json['data']['lots'][1]['guarantee']['amount'], 100500)
        self.assertEqual(response.json['data']['lots'][1]['guarantee']['currency'], "EUR")
        self.assertEqual(response.json['data']['lots'][2]['guarantee']['amount'], 20)
        self.assertEqual(response.json['data']['lots'][2]['guarantee']['currency'], "EUR")
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': lot}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'Lot id should be uniq for all lots'], u'location': u'body', u'name': u'lots'}
        ])

    def test_patch_tender_lot(self):
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']

        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'],
                                                                                 self.tender_token),
                                       {"data": {"title": "new title"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["title"], "new title")

        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                                 lot['id'],
                                                                                 self.tender_token),
                                       {"data": {"guarantee": {"amount": 12}}})
        self.assertEqual(response.status, '200 OK')
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 12)
        self.assertEqual(response.json['data']['guarantee']['currency'], 'UAH')

        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                                 lot['id'],
                                                                                 self.tender_token),
                                       {"data": {"guarantee": {"currency": "USD"}}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['guarantee']['currency'], 'UAH')

        response = self.app.patch_json('/tenders/{}/lots/some_id'.format(self.tender_id),
                                       {"data": {"title": "other title"}},
                                       status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'lot_id'}
        ])

        response = self.app.patch_json('/tenders/some_id/lots/some_id',
                                       {"data": {"title": "other title"}},
                                       status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["title"], "new title")

        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'],
                                                                                 self.tender_token),
                                       {"data": {"title": "other title"}}, status=403)

        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't update lot in current (unsuccessful) tender status")

    def test_patch_tender_currency(self):
        # create lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertEqual(lot['value']['currency'], "UAH")

        # update tender currency without mimimalStep currency change
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"value": {"currency": "GBP"}}}, status=422)

        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'currency should be identical to currency of value of tender'],
             u'location': u'body', u'name': u'minimalStep'}
        ])

        # update tender currency
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"value": {"currency": "GBP"},
                                                 "minimalStep": {"currency": "GBP"}}
                                        })
        self.assertEqual(response.status, '200 OK')
        # log currency is updated too
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertEqual(lot['value']['currency'], "GBP")

        # try to update lot currency
        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                                 lot['id'],
                                                                                 self.tender_token),
                                       {"data": {"value": {"currency": "USD"}}})
        self.assertEqual(response.status, '200 OK')
        # but the value stays unchanged
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertEqual(lot['value']['currency'], "GBP")

        # try to update minimalStep currency
        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                                 lot['id'],
                                                                                 self.tender_token),
                                       {"data": {"minimalStep": {"currency": "USD"}}})
        self.assertEqual(response.status, '200 OK')
        # but the value stays unchanged
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertEqual(lot['minimalStep']['currency'], "GBP")

        # try to update lot minimalStep currency and lot value currency in single request
        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                                 lot['id'],
                                                                                 self.tender_token),
                                       {"data": {"value": {"currency": "USD"},
                                                 "minimalStep": {"currency": "USD"}}})
        self.assertEqual(response.status, '200 OK')
        # but the value stays unchanged
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertEqual(lot['value']['currency'], "GBP")
        self.assertEqual(lot['minimalStep']['currency'], "GBP")

    def test_patch_tender_vat(self):
        # set tender VAT
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"value": {"valueAddedTaxIncluded": True}}})

        self.assertEqual(response.status, '200 OK')

        # create lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertTrue(lot['value']['valueAddedTaxIncluded'])

        # update tender VAT
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token), {
            "data": {"value": {"valueAddedTaxIncluded": False}, "minimalStep": {"valueAddedTaxIncluded": False}}})

        self.assertEqual(response.status, '200 OK')
        # log VAT is updated too
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertFalse(lot['value']['valueAddedTaxIncluded'])

        # try to update lot VAT
        response = self.app.patch_json(
            '/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token),
            {"data": {"value": {"valueAddedTaxIncluded": True}}})
        self.assertEqual(response.status, '200 OK')
        # but the value stays unchanged
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertFalse(lot['value']['valueAddedTaxIncluded'])

        # try to update minimalStep VAT
        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                                 lot['id'],
                                                                                 self.tender_token),
                                       {"data": {"minimalStep": {"valueAddedTaxIncluded": True}}})
        self.assertEqual(response.status, '200 OK')
        # but the value stays unchanged
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertFalse(lot['minimalStep']['valueAddedTaxIncluded'])

        # try to update minimalStep VAT and value VAT in single request
        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                                 lot['id'],
                                                                                 self.tender_token),
                                       {"data": {"value": {"valueAddedTaxIncluded": True},
                                                 "minimalStep": {"valueAddedTaxIncluded": True}}})
        self.assertEqual(response.status, '200 OK')
        # but the value stays unchanged
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertFalse(lot['value']['valueAddedTaxIncluded'])
        self.assertEqual(lot['minimalStep']['valueAddedTaxIncluded'], lot['value']['valueAddedTaxIncluded'])

    def test_get_tender_lot(self):
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']

        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(set(response.json['data']), set([u'id', u'title', u'date', u'description',
                                                          u'value', u'status', u'minimalStep']))

        self.set_status('active.qualification')

        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
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

    def test_get_tender_lots(self):
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']

        response = self.app.get('/tenders/{}/lots'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'title', u'date', u'description',
                                                             u'value', u'status', u'minimalStep']))

        self.set_status('active.qualification')

        response = self.app.get('/tenders/{}/lots'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'][0], lot)

        response = self.app.get('/tenders/some_id/lots', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

    def test_delete_tender_lot(self):
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']

        response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'],
                                                                             self.tender_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], lot)

        response = self.app.delete('/tenders/{}/lots/some_id?acc_token={}'.format(self.tender_id, self.tender_token),
                                   status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'lot_id'}
        ])

        response = self.app.delete('/tenders/some_id/lots/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"items": [{'relatedLot': lot['id']}]}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'],
                                                                             self.tender_token),
                                   status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'relatedLot': [u'relatedLot should be one of lots']}],
             u'location': u'body',
             u'name': u'items'}
        ])
        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'],
                                                                             self.tender_token),
                                   status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't delete lot in current (unsuccessful) tender status")

    def test_tender_lot_guarantee(self):
        data = deepcopy(test_tender_data)
        data['guarantee'] = {"amount": 100, "currency": "USD"}
        response = self.app.post_json('/tenders', {'data': data})
        tender = response.json['data']
        owner_token = response.json['access']['token']
        self.assertEqual(response.status, '201 Created')
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 100)
        self.assertEqual(response.json['data']['guarantee']['currency'], "USD")

        lot = deepcopy(test_lots[0])
        lot['guarantee'] = {"amount": 20, "currency": "USD"}
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender['id'], owner_token), {'data': lot})
        self.assertEqual(response.status, '201 Created')
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 20)
        self.assertEqual(response.json['data']['guarantee']['currency'], "USD")

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                       {'data': {'guarantee': {"currency": "GBP"}}})
        self.assertEqual(response.status, '200 OK')
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 20)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        lot['guarantee'] = {"amount": 20, "currency": "GBP"}
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender['id'], owner_token), {'data': lot})
        self.assertEqual(response.status, '201 Created')
        lot_id = response.json['data']['id']
        self.assertEqual(response.json['data']['guarantee']['amount'], 20)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        response = self.app.get('/tenders/{}'.format(tender['id']))
        self.assertEqual(response.json['data']['guarantee']['amount'], 20 + 20)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        lot2 = deepcopy(test_lots[0])
        lot2['guarantee'] = {"amount": 30, "currency": "GBP"}
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender['id'], owner_token), {'data': lot2})
        self.assertEqual(response.status, '201 Created')
        lot2_id = response.json['data']['id']
        self.assertEqual(response.json['data']['guarantee']['amount'], 30)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        lot2['guarantee'] = {"amount": 40, "currency": "USD"}
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender['id'], owner_token), {'data': lot2},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'lot guarantee currency should be identical to tender guarantee currency'],
             u'location': u'body',
             u'name': u'lots'}
        ])

        response = self.app.get('/tenders/{}'.format(tender['id']))
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 20 + 20 + 30)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token),
                                       {"data": {"guarantee": {"amount": 55}}})
        self.assertEqual(response.json['data']['guarantee']['amount'], 20 + 20 + 30)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(tender['id'], lot2_id, owner_token),
                                       {'data': {'guarantee': {"amount": 35, "currency": "GBP"}}})
        self.assertEqual(response.json['data']['guarantee']['amount'], 35)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        response = self.app.get('/tenders/{}'.format(tender['id']))
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 20 + 20 + 35)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        for l_id in (lot_id, lot2_id):
            response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(tender['id'], l_id, owner_token),
                                           {'data': {'guarantee': {"amount": 0, "currency": "GBP"}}})
            self.assertEqual(response.json['data']['guarantee']['amount'], 0)
            self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        response = self.app.get('/tenders/{}'.format(tender['id']))
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 20)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        for l_id in (lot_id, lot2_id):
            response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(tender['id'], l_id, owner_token))
            self.assertEqual(response.status, '200 OK')

        response = self.app.get('/tenders/{}'.format(tender['id']))
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 20)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")


class CompetitiveDialogueUALotEdgeCasesTest(CompetitiveDialogueEULotEdgeCasesTest):
    initial_data = test_tender_data_ua


class CompetitiveDialogueUALotFeatureResourceTest(BaseCompetitiveDialogUAContentWebTest):
    initial_lots = 2 * test_lots
    initial_auth = ('Basic', ('broker', ''))

    def test_tender_value(self):
        request_path = '/tenders/{}'.format(self.tender_id)
        response = self.app.get(request_path)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['value']['amount'], sum([i['value']['amount'] for i in self.initial_lots]))

    def test_tender_features_invalid(self):
        request_path = '/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token)
        data = test_tender_data.copy()
        item = data['items'][0].copy()
        item['id'] = "1"
        data['items'] = [item]
        data['features'] = [
            {
                "featureOf": "lot",
                "relatedItem": self.initial_lots[0]['id'],
                "title": u"Потужність всмоктування",
                "enum": [
                    {
                        "value": 1.0,
                        "title": u"До 1000 Вт"
                    },
                    {
                        "value": 0.15,
                        "title": u"Більше 1000 Вт"
                    }
                ]
            }
        ]
        response = self.app.patch_json(request_path, {'data': data}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'enum': [{u'value': [u'Float value should be less than 0.99.']}]}],
             u'location': u'body',
             u'name': u'features'}
        ])
        data['features'][0]["enum"][0]["value"] = 0.3
        data['features'].append(data['features'][0].copy())
        data['features'][1]["enum"][0]["value"] = 0.3
        data['features'].append(data['features'][0].copy())
        data['features'][2]["enum"][0]["value"] = 0.3
        data['features'].append(data['features'][0].copy())
        data['features'][3]["enum"][0]["value"] = 0.3
        response = self.app.patch_json(request_path, {'data': data}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [
                u'Sum of max value of all features for lot should be less then or equal to {:.0f}%'.format(
                    FEATURES_MAX_SUM * 100)],
             u'location': u'body',
             u'name': u'features'}
        ])
        data['features'][1]["enum"][0]["value"] = 0.1
        data['features'].append(data['features'][0].copy())
        data['features'][2]["relatedItem"] = self.initial_lots[1]['id']
        data['features'].append(data['features'][2].copy())
        response = self.app.patch_json(request_path, {'data': data})
        self.assertEqual(response.status, '200 OK')


class CompetitiveDialogueUALotBidderResourceTest(BaseCompetitiveDialogUAContentWebTest):
    initial_lots = test_lots
    initial_auth = ('Basic', ('broker', ''))

    def test_create_tender_bidder_invalid(self):
        request_path = '/tenders/{}/bids'.format(self.tender_id)
        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers']}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'lotValues'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers'],
                                                              'lotValues': [{"value": {"amount": 500}}]}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'relatedLot': [u'This field is required.']}],
             u'location': u'body',
             u'name': u'lotValues'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers'],
                                                              'lotValues': [{"value": {"amount": 500},
                                                                             'relatedLot': "0" * 32}]}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'relatedLot': [u'relatedLot should be one of lots']}], u'location': u'body', u'name': u'lotValues'}
        ])

        # Field 'value' doesn't exists on first stage
        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers'],
                                                              'lotValues': [{"value": {"amount": 5000000},
                                                                             'relatedLot': self.initial_lots[0]['id']}]}
                                                     })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers'],
                                                              'lotValues': [{"value": {"amount": 500,
                                                                                       'valueAddedTaxIncluded': False},
                                                                             'relatedLot': self.initial_lots[0]['id']}]}
                                                     })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers'],
                                                              'lotValues': [{"value": {"amount": 500,
                                                                                       'currency': "USD"},
                                                                             'relatedLot': self.initial_lots[0]['id']}]}
                                                     })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers'],
                                                              "value": {"amount": 500},
                                                              'lotValues': [{"value": {"amount": 500},
                                                                             'relatedLot': self.initial_lots[0]['id']}]}
                                                     })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

    def test_patch_tender_bidder(self):
        lot_id = self.initial_lots[0]['id']
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True,
                                                'selfQualified': True,
                                                'tenderers': test_bids[0]["tenderers"],
                                                'lotValues': [{"value": {"amount": 500},
                                                               'relatedLot': lot_id}]}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bidder = response.json['data']
        bid_token = response.json['access']['token']
        lot = bidder['lotValues'][0]

        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bidder['id'], bid_token),
                                       {"data": {'tenderers': [{"name": u"Державне управління управлінням справами"}]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lotValues'][0]['date'], lot['date'])
        self.assertNotEqual(response.json['data']['tenderers'][0]['name'], bidder['tenderers'][0]['name'])

        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bidder['id'], bid_token),
                                       {"data": {'lotValues': [{"value": {"amount": 500},
                                                                'relatedLot': lot_id}],
                                                 'tenderers': test_bids[0]["tenderers"]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lotValues'][0]['date'], lot['date'])
        self.assertEqual(response.json['data']['tenderers'][0]['name'], bidder['tenderers'][0]['name'])

        # If we don't change anything then we get null
        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bidder['id'], bid_token),
                                       {"data": {'lotValues': [{"value": {"amount": 400}, 'relatedLot': lot_id}]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bidder['id'], bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertNotIn('lotValues', response.json['data'])

        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bidder['id'], bid_token),
                                       {"data": {'lotValues': [{"value": {"amount": 500},
                                                                'relatedLot': lot_id}],
                                                 'status': 'active'}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update bid in current (unsuccessful) tender status")


class CompetitiveDialogueUALotFeatureBidderResourceTest(BaseCompetitiveDialogUAContentWebTest):
    initial_lots = test_lots
    initial_auth = ('Basic', ('broker', ''))

    def setUp(self):
        super(CompetitiveDialogueUALotFeatureBidderResourceTest, self).setUp()
        self.lot_id = self.initial_lots[0]['id']
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token), {"data": {
            "items": [
                {
                    'relatedLot': self.lot_id,
                    'id': '1'
                }
            ],
            "features": [
                {
                    "code": "code_item",
                    "featureOf": "item",
                    "relatedItem": "1",
                    "title": u"item feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                },
                {
                    "code": "code_lot",
                    "featureOf": "lot",
                    "relatedItem": self.lot_id,
                    "title": u"lot feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                },
                {
                    "code": "code_tenderer",
                    "featureOf": "tenderer",
                    "title": u"tenderer feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                }
            ]
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['items'][0]['relatedLot'], self.lot_id)

    def test_create_tender_bidder_invalid(self):
        request_path = '/tenders/{}/bids'.format(self.tender_id)
        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers']}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')

        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers'],
                                                              'lotValues': [{"value": {"amount": 500}}]}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'relatedLot': [u'This field is required.']}], u'location': u'body', u'name': u'lotValues'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers'],
                                                              'lotValues': [{"value": {"amount": 500},
                                                                             'relatedLot': "0" * 32}]}},
                                    status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'relatedLot': [u'relatedLot should be one of lots']}],
             u'location': u'body',
             u'name': u'lotValues'}
        ])

        # Field 'value' doesn't exists on first stage
        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers'],
                                                              'lotValues': [{"value": {"amount": 5000000},
                                                                             'relatedLot': self.lot_id}]}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers'],
                                                              'lotValues': [{"value": {"amount": 500,
                                                                                       'valueAddedTaxIncluded': False},
                                                                             'relatedLot': self.lot_id}]}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]['tenderers'],
                                                              'lotValues': [{"value": {"amount": 500,
                                                                                       'currency': "USD"},
                                                                             'relatedLot': self.lot_id}]}})
        self.assertEqual(response.status, '201 Created')

    def test_create_tender_bidder(self):
        request_path = '/tenders/{}/bids'.format(self.tender_id)
        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]["tenderers"],
                                                              'lotValues': [{"value": {"amount": 500},
                                                                             'relatedLot': self.lot_id}],
                                                              'parameters': [{"code": "code_item", "value": 0.01},
                                                                             {"code": "code_tenderer", "value": 0.01},
                                                                             {"code": "code_lot", "value": 0.01}]}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bidder = response.json['data']
        self.assertEqual(bidder['tenderers'][0]['name'], test_tender_data["procuringEntity"]['name'])
        self.assertIn('id', bidder)
        self.assertIn(bidder['id'], response.headers['Location'])

        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': test_bids[0]["tenderers"],
                                                              'lotValues': [{"value": {"amount": 500},
                                                                             'relatedLot': self.lot_id}],
                                                              'parameters': [{"code": "code_item", "value": 0.01},
                                                                             {"code": "code_tenderer", "value": 0.01},
                                                                             {"code": "code_lot", "value": 0.01}]}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add bid in current (unsuccessful) tender status")


class CompetitiveDialogueUALotProcessTest(BaseCompetitiveDialogUAContentWebTest):

    def test_1lot_0bid(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # create tender
        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        # add lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                      {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        lot_id = response.json['data']['id']
        # add relatedLot for item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [{'relatedLot': lot_id}]}})
        self.assertEqual(response.status, '200 OK')
        # switch to active.tendering
        response = self.set_status('active.tendering')
        self.assertNotIn("auctionPeriod", response.json['data']['lots'][0])
        # switch to unsuccessful
        response = self.set_status('active.stage2.pending', {'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(tender_id), {"data": {"id": tender_id}})
        self.assertEqual(response.json['data']["lots"][0]['status'], 'unsuccessful')
        self.assertEqual(response.json['data']['status'], 'unsuccessful')

        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                      {'data': test_lots[0]},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [{
            "location": "body", "name": "data", "description": "Can't add lot in current (unsuccessful) tender status"
        }])

    def test_1lot_1bid(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # create tender
        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        # add lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                      {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        lot_id = response.json['data']['id']
        # add relatedLot for item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [{'relatedLot': lot_id}]}})
        self.assertEqual(response.status, '200 OK')
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True,
                                                'selfQualified': True,
                                                'tenderers': test_bids[0]["tenderers"],
                                                'lotValues': [{"value": {"amount": 500},
                                                               'relatedLot': lot_id}]}})
        # switch to active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.check_chronograph()
        # switch to unsuccessful
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}?acc_token={}'.format(tender_id, owner_token))
        self.assertEqual(response.json['data']['status'], 'unsuccessful')

    def test_1lot_2bid_1unqualified(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # create tender
        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        # add lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                      {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        lot_id = response.json['data']['id']
        # add relatedLot for item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [{'relatedLot': lot_id}]}})
        self.assertEqual(response.status, '200 OK')
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        bidder_data = deepcopy(test_bids[0]['tenderers'][0])
        bidder_data['identifier']['id'] = u"00037256"
        self.app.post_json('/tenders/{}/bids'.format(tender_id),
                           {'data': {'selfEligible': True,
                                     'selfQualified': True,
                                     'tenderers': [bidder_data],
                                     'lotValues': [{"value": {"amount": 500},
                                     'relatedLot': lot_id}]}})

        bidder_data['identifier']['id'] = u"00037257"
        self.app.post_json('/tenders/{}/bids'.format(tender_id),
                           {'data': {'selfEligible': True,
                                     'selfQualified': True,
                                     'tenderers': [bidder_data],
                                     'lotValues': [{"value": {"amount": 500},
                                     'relatedLot': lot_id}]}})
        bidder_data['identifier']['id'] = u"00037258"
        self.app.post_json('/tenders/{}/bids'.format(tender_id),
                           {'data': {'selfEligible': True,
                                     'selfQualified': True,
                                     'tenderers': [bidder_data],
                                     'lotValues': [{"value": {"amount": 500},
                                                    'relatedLot': lot_id}]}})
        # switch to active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']

        response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                           qualifications[0]['id'],
                                                                                           owner_token),
                                       {"data": {'status': 'active', "qualified": True, "eligible": True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active')

        response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                           qualifications[1]['id'],
                                                                                           owner_token),
                                       {"data": {'status': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'unsuccessful')
        response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                           qualifications[2]['id'],
                                                                                           owner_token),
                                       {"data": {'status': 'active', "qualified": True, "eligible": True}})

        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active')
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "active.pre-qualification.stand-still")

    def test_1lot_2bid(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # create tender
        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        # add lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                      {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        lot_id = response.json['data']['id']
        self.initial_lots = [response.json['data']]
        # add relatedLot for item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [{'relatedLot': lot_id}]}})
        self.assertEqual(response.status, '200 OK')
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        bidder_data = deepcopy(test_bids[0]['tenderers'][0])
        bidder_data['identifier']['id'] = u"00037256"
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True,
                                                'selfQualified': True,
                                                'tenderers': [bidder_data],
                                                'lotValues': [{"value": {"amount": 450},
                                                               'relatedLot': lot_id}]}})
        bid_id = response.json['data']['id']
        bid_token = response.json['access']['token']
        # create second bid
        self.app.authorization = ('Basic', ('broker', ''))
        bidder_data['identifier']['id'] = u"00037257"
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True,
                                                'selfQualified': True,
                                                'tenderers': [bidder_data],
                                                'lotValues': [{"value": {"amount": 475},
                                                               'relatedLot': lot_id}]}})
        bidder_data['identifier']['id'] = u"00037258"
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True,
                                                'selfQualified': True,
                                                'tenderers': [bidder_data],
                                                'lotValues': [{"value": {"amount": 470},
                                                               'relatedLot': lot_id}]}})
        # switch to active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']
        for qualification in qualifications:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                               qualification['id'],
                                                                                               owner_token),
                                      {"data": {'status': 'active', "qualified": True, "eligible": True}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active')

        response = self.app.get('/tenders/{}?acc_token={}'.format(tender_id, owner_token))
        self.assertEqual(response.status, '200 OK')

        for bid in response.json['data']['bids']:
            self.assertEqual(bid['status'], 'active')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")
        self.check_chronograph()

        response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token))
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.status, "200 OK")

    def test_2lot_2bid_1lot_del(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # create tender
        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        lots = []
        for lot in 2 * test_lots:
            # add lot
            response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                          {'data': test_lots[0]})
            self.assertEqual(response.status, '201 Created')
            lots.append(response.json['data']['id'])
        self.initial_lots = lots
        # add item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [test_tender_data['items'][0] for i in lots]}})

        response = self.set_status('active.tendering')
        # create bid

        bids = []
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True,
                                                'selfQualified': True,
                                                'tenderers': test_bids[0]["tenderers"],
                                                'lotValues': [{"value": {"amount": 500}, 'relatedLot': lot_id}
                                                              for lot_id in lots
                                                              ]}})
        bids.append(response.json)
        # create second bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                                'tenderers': test_bids[1]["tenderers"],
                                                'lotValues': [{"value": {"amount": 500}, 'relatedLot': lot_id}
                                                              for lot_id in lots
                                                              ]}})
        bids.append(response.json)
        response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lots[0], owner_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

    def test_1lot_3bid_1del(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # create tender
        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        # add lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                      {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        lot_id = response.json['data']['id']
        self.initial_lots = [response.json['data']]
        # add relatedLot for item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [{'relatedLot': lot_id}]}})
        self.assertEqual(response.status, '200 OK')
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        bids = []
        bidder_data = deepcopy(test_bids[0]['tenderers'][0])
        self.assertEqual(len(test_bids), 3)
        for index, test_bid in enumerate(test_bids):
            bidder_data['identifier']['id'] = (00037256+index)
            response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                          {'data': {'selfEligible': True,
                                                    'selfQualified': True,
                                                    'tenderers': [bidder_data],
                                                    'lotValues': [{"value": {"amount": 450},
                                                                   'relatedLot': lot_id}]}})
            bids.append({response.json['data']['id']: response.json['access']['token']})

        response = self.app.delete('/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bids[2].keys()[0],
                                                                             bids[2].values()[0]))
        self.assertEqual(response.status, '200 OK')
        # switch to active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token))
        self.assertTrue(all([i['status'] == 'unsuccessful' for i in response.json['data']['lots']]))
        self.assertEqual(response.json['data']['status'], 'unsuccessful')

    def test_1lot_3bid_1un(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # create tender
        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        # add lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token), {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        lot_id = response.json['data']['id']
        self.initial_lots = [response.json['data']]
        # add relatedLot for item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [{'relatedLot': lot_id}]}})
        self.assertEqual(response.status, '200 OK')
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        bids = []
        for i in range(3):
            bidder_data = deepcopy(test_bids[0]['tenderers'][0])
            bidder_data['identifier']['id'] = str(00037256+i)
            response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                          {'data': {'selfEligible': True, 'selfQualified': True,
                                                    'tenderers': [bidder_data],
                                                    'lotValues': [{"value": {"amount": 450},
                                                                   'relatedLot': lot_id}]}})
            bids.append({response.json['data']['id']: response.json['access']['token']})

        # switch to active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']
        for qualification in qualifications:
            if qualification['bidID'] == bids[2].keys()[0]:
                response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                                   qualification['id'],
                                                                                                   owner_token),
                                          {"data": {'status': 'unsuccessful'}})
                self.assertEqual(response.status, '200 OK')
                self.assertEqual(response.json['data']['status'], 'unsuccessful')
            else:
                response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                                   qualification['id'],
                                                                                                   owner_token),
                                          {"data": {'status': 'active', "qualified": True, "eligible": True}})
                self.assertEqual(response.status, '200 OK')
                self.assertEqual(response.json['data']['status'], 'active')
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")
        self.check_chronograph()

        response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, owner_token))
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.status, "200 OK")

        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']

    def test_2lot_0bid(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # create tender
        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        lots = []
        for lot in 2 * test_lots:
            # add lot
            response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                          {'data': test_lots[0]})
            self.assertEqual(response.status, '201 Created')
            lots.append(response.json['data']['id'])
        # add item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [test_tender_data['items'][0] for i in lots]}})
        # add relatedLot for item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [{'relatedLot': i} for i in lots]}})
        self.assertEqual(response.status, '200 OK')

        self.time_shift('active.pre-qualification')
        self.check_chronograph()
        # switch to unsuccessful
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}?acc_token={}'.format(tender_id, owner_token))
        self.assertTrue(all([i['status'] == 'unsuccessful' for i in response.json['data']['lots']]))
        self.assertEqual(response.json['data']['status'], 'unsuccessful')

    def test_2lot_2can(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # create tender
        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        lots = []
        for lot in 2 * test_lots:
            # add lot
            response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                          {'data': test_lots[0]})
            self.assertEqual(response.status, '201 Created')
            lots.append(response.json['data']['id'])
        # add item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [test_tender_data['items'][0] for i in lots]}})
        # add relatedLot for item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [{'relatedLot': i} for i in lots]}})
        self.assertEqual(response.status, '200 OK')
        # cancel every lot
        for lot_id in lots:
            response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(tender_id, owner_token),
                                          {'data': {'reason': 'cancellation reason',
                                                    'status': 'active',
                                                    "cancellationOf": "lot",
                                                    "relatedLot": lot_id}})
        response = self.app.get('/tenders/{}'.format(tender_id))
        self.assertTrue(all([i['status'] == 'cancelled' for i in response.json['data']['lots']]))
        self.assertEqual(response.json['data']['status'], 'cancelled')

    def test_2lot_1can(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # create tender
        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        lots = []
        for lot in 2 * test_lots:
            # add lot
            response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                          {'data': test_lots[0]})
            self.assertEqual(response.status, '201 Created')
            lots.append(response.json['data']['id'])
        # add item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [test_tender_data['items'][0] for i in lots]}})
        # add relatedLot for item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [{'relatedLot': i} for i in lots]}})
        self.assertEqual(response.status, '200 OK')
        # cancel first lot
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(tender_id, owner_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'active',
                                                "cancellationOf": "lot",
                                                "relatedLot": lots[0]}})

        response = self.app.get('/tenders/{}'.format(tender_id))
        self.assertFalse(all([i['status'] == 'cancelled' for i in response.json['data']['lots']]))
        self.assertTrue(any([i['status'] == 'cancelled' for i in response.json['data']['lots']]))
        self.assertEqual(response.json['data']['status'], 'active.tendering')

        # try to restore lot back by old cancellation
        response = self.app.get('/tenders/{}/cancellations?acc_token={}'.format(tender_id, owner_token))
        self.assertEqual(len(response.json['data']), 1)
        cancellation = response.json['data'][0]
        self.assertEqual(cancellation['status'], 'active')

        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(tender_id, cancellation['id'],
                                                                                          owner_token),
                                      {'data': {'status': 'pending'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'][0]["description"], "Can update cancellation only in active lot status")

        # try to restore lot back by new pending cancellation
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(tender_id, owner_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'pending',
                                                "cancellationOf": "lot",
                                                "relatedLot": lots[0]}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'][0]["description"], "Can add cancellation only in active lot status")
        response = self.app.get('/tenders/{}'.format(tender_id))
        self.assertFalse(all([i['status'] == 'cancelled' for i in response.json['data']['lots']]))
        self.assertTrue(any([i['status'] == 'cancelled' for i in response.json['data']['lots']]))
        self.assertEqual(response.json['data']['status'], 'active.tendering')

    def test_2lot_2bid_0com_1can(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # create tender
        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        lots = []
        for lot in 2 * test_lots:
            # add lot
            response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                          {'data': test_lots[0]})
            self.assertEqual(response.status, '201 Created')
            lots.append(response.json['data']['id'])
        # add item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [test_tender_data['items'][0] for i in lots]}})
        # add relatedLot for item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [{'relatedLot': i} for i in lots]}})
        self.assertEqual(response.status, '200 OK')
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        bidder_data = deepcopy(test_bids[0]['tenderers'][0])
        bidder_data['identifier']['id'] = u"00037256"
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True,
                                                'selfQualified': True,
                                                'tenderers': [bidder_data],
                                                'lotValues': [{"value": {"amount": 500}, 'relatedLot': lot_id}
                                                              for lot_id in lots]}})
        bidder_data['identifier']['id'] = u"00037257"
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True,
                                                'selfQualified': True,
                                                'tenderers': [bidder_data],
                                                'lotValues': [{"value": {"amount": 499}, 'relatedLot': lot_id}
                                                              for lot_id in lots]}})

        bidder_data['identifier']['id'] = u"00037258"
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True,
                                                'selfQualified': True,
                                                'tenderers': [bidder_data],
                                                'lotValues': [{"value": {"amount": 499}, 'relatedLot': lot_id}
                                                              for lot_id in lots]}})

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(tender_id, owner_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'active',
                                                "cancellationOf": "lot",
                                                "relatedLot": lots[0]}})
        response = self.app.get('/tenders/{}?acc_token={}'.format(tender_id, owner_token))
        self.assertEqual(response.status, "200 OK")
        # active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']
        self.assertEqual(len(qualifications), 3)

        for qualification in qualifications:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                               qualification['id'],
                                                                                               owner_token),
                                      {"data": {'status': 'active', "qualified": True, "eligible": True}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active')
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")


    def test_2lot_2bid_2com_2win(self):
        self.app.authorization = ('Basic', ('broker', ''))
        # create tender
        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        lots = []
        for lot in 2 * test_lots:
            # add lot
            response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                                          {'data': test_lots[0]})
            self.assertEqual(response.status, '201 Created')
            lots.append(response.json['data']['id'])
        self.initial_lots = lots
        # add item
        self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                            {"data": {"items": [test_tender_data['items'][0] for i in lots]}})
        # add relatedLot for item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"items": [{'relatedLot': i} for i in lots]}})
        self.assertEqual(response.status, '200 OK')
        # create bid
        bidder_data = deepcopy(test_bids[1]['tenderers'][0])
        bidder_data['identifier']['id'] = u"00037256"
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.post_json('/tenders/{}/bids'.format(tender_id),
                          {'data': {'selfEligible': True,
                                    'selfQualified': True,
                                    'tenderers': [bidder_data],
                                    'lotValues': [{"value": {"amount": 500}, 'relatedLot': lot_id}
                                                  for lot_id in lots]}})
        # create second bid
        bidder_data['identifier']['id'] = u"00037257"
        self.app.post_json('/tenders/{}/bids'.format(tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                                                           'tenderers': [bidder_data],
                                                                           'lotValues': [{"value": {"amount": 500},
                                                                                          'relatedLot': lot_id}
                                                                                         for lot_id in lots]}})
        # create third bid
        bidder_data['identifier']['id'] = u"00037258"
        self.app.post_json('/tenders/{}/bids'.format(tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                                                           'tenderers': [bidder_data],
                                                                           'lotValues': [{"value": {"amount": 500},
                                                                                          'relatedLot': lot_id}
                                                                                         for lot_id in lots]}})
        # switch to active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.check_chronograph()
        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']
        self.assertEqual(len(qualifications), 6)

        for qualification in qualifications:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                               qualification['id'],
                                                                                               owner_token),
                                      {"data": {'status': 'active', "qualified": True, "eligible": True}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active')
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CompetitiveDialogueEULotResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogueEULotBidderResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogueEULotFeatureResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogueEULotFeatureBidderResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogueEULotProcessTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogueUALotResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogueUALotFeatureResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogueUALotBidderResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogueUALotProcessTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogueUALotFeatureBidderResourceTest))

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
