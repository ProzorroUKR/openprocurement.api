# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy
from datetime import timedelta
from uuid import uuid4
from copy import deepcopy
from openprocurement.api.models import get_now
from openprocurement.api.tests.base import test_organization
from openprocurement.tender.openeu.tests.base import BaseTenderContentWebTest, BaseTenderWebTest, test_tender_data, test_lots, test_bids
from openprocurement.tender.competitivedialogue.tests.base import (BaseCompetitiveDialogEUStage2ContentWebTest,
                                                                   BaseCompetitiveDialogUAStage2ContentWebTest,
                                                                   BaseCompetitiveDialogEUWebTest,
                                                                   test_tender_stage2_data_ua,
                                                                   test_tender_stage2_data_eu)


class TenderStage2EULotResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):

    initial_auth = ('Basic', ('broker', ''))
    initial_lots = [deepcopy(test_lots[0]) for i in range(3)]

    def setUp(self):
        super(BaseCompetitiveDialogEUStage2ContentWebTest, self).setUp()
        self.app.authorization = ('Basic', ('broker', ''))

    def test_create_tender_lot_invalid(self):
        """ Try create invalid lot """
        self.create_tender()
        response = self.app.post_json('/tenders/some_id/lots', {'data': {'title': 'lot title', 'description': 'lot description'}}, status=404)
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
            {u'description':
                u"Content-Type header should be one of ['application/json']", u'location': u'header', u'name': u'Content-Type'}
        ])

        response = self.app.post(request_path, 'data', content_type='application/json', status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u"location": u"body",
             u"name": u"data",
             u"description": u"Can't create lot for tender stage2"}
        ])

        response = self.app.post_json(request_path, 'data', status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u"location": u"body",
             u"name": u"data",
             u"description": u"Can't create lot for tender stage2"}
        ])

        response = self.app.post_json(request_path, {'not_data': {}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u"location": u"body",
             u"name": u"data",
             u"description": u"Can't create lot for tender stage2"}
        ])

        response = self.app.post_json(request_path, {'data': {}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u"location": u"body",
             u"name": u"data",
             u"description": u"Can't create lot for tender stage2"}
        ])

        response = self.app.post_json(request_path, {'data': {'invalid_field': 'invalid_value'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u"location": u"body",
             u"name": u"data",
             u"description": u"Can't create lot for tender stage2"}
        ])

        response = self.app.post_json(request_path, {'data': {'value': 'invalid_value'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u"location": u"body",
             u"name": u"data",
             u"description": u"Can't create lot for tender stage2"}
        ])

        response = self.app.post_json(request_path, {'data': {
            'title': 'lot title',
            'description': 'lot description',
            'value': {'amount': '100.0'},
            'minimalStep': {'amount': '500.0'},
        }}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u"location": u"body",
             u"name": u"data",
             u"description": u"Can't create lot for tender stage2"}
        ])

    def test_patch_tender_lot(self):
        """ Patch tender lot which came from first stage """
        self.create_tender()
        lot_id = self.lots_id[0]

        # Add new title
        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot_id,
                                                                                 self.tender_token),
                                       {"data": {"title": "new title"}}, status=403)

        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u"location": u"body",
             u"name": u"data",
             u"description": u"Can't update lot for tender stage2"}
        ])

        # Change guarantee currency
        self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot_id, self.tender_token),
                            {"data": {"guarantee": {"amount": 123, "currency": "USD"}}},
                            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u"location": u"body",
             u"name": u"data",
             u"description": u"Can't update lot for tender stage2"}
        ])

        # Try get lot with bad lot id
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

        # Try get lot with bad tender id and lot id
        response = self.app.patch_json('/tenders/some_id/lots/some_id', {"data": {"title": "other title"}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        # Change title for lot when tender has status active.tendering
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertNotEqual(response.json['data']["title"], "new title")

        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        # Try change title for lot when tender in status active.pre-quaifications
        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot_id,
                                                                                 self.tender_token),
                                       {"data": {"title": "other title"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [{u"location": u"body",
                                                    u"name": u"data",
                                                    u"description": u"Can't update lot for tender stage2"}])

    def test_patch_tender_currency(self):
        self.create_tender()
        lot = self.lots[0]
        self.assertEqual(lot['value']['currency'], "UAH")

        # update tender currency without mimimalStep currency change
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {'data': {'value': {'currency': 'GBP'}}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.json['errors'],
                         [{u'description': [u'currency should be identical to currency of value of tender'],
                           u'location': u'body',
                           u'name': u'minimalStep'}])

        # try update tender currency
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {'data': {'value': {'currency': 'GBP'},
                                                 'minimalStep': {'currency': 'GBP'}}})
        # log currency is updated too
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertEqual(lot['value']['currency'], "UAH")

        # try to update lot currency
        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token),
                                       {"data": {"value": {"currency": "USD"}}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [{u"location": u"body",
                                                    u"name": u"data",
                                                    u"description": u"Can't update lot for tender stage2"}])
        # but the value stays unchanged
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertEqual(lot['value']['currency'], "UAH")  # it's still UAH

        # try to update minimalStep currency
        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token),
                                       {"data": {"minimalStep": {"currency": "USD"}}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [{u"location": u"body",
                                                    u"name": u"data",
                                                    u"description": u"Can't update lot for tender stage2"}])
        # but the value stays unchanged
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertEqual(lot['minimalStep']['currency'], "UAH")

        # try to update lot minimalStep currency and lot value currency in single request
        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token),
                                       {"data": {"value": {"currency": "USD"}, "minimalStep": {"currency": "USD"}}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [{u"location": u"body",
                                                    u"name": u"data",
                                                    u"description": u"Can't update lot for tender stage2"}])
        # but the value stays unchanged
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertEqual(lot['value']['currency'], "UAH")
        self.assertEqual(lot['minimalStep']['currency'], "UAH")

    def test_patch_tender_vat(self):
        # set tender VAT
        data = deepcopy(self.initial_data)
        data['value']['valueAddedTaxIncluded'] = True
        self.create_tender(initial_data=data)

        response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token))
        lot = response.json['data']['lots'][0]
        self.assertTrue(lot['value']['valueAddedTaxIncluded'])

        # Try update tender VAT
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {'data': {'value': {'valueAddedTaxIncluded': False},
                                                 'minimalStep': {'valueAddedTaxIncluded': False}}
                                        })
        self.assertEqual(response.status, '200 OK')
        # log VAT is not updated too
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertTrue(lot['value']['valueAddedTaxIncluded'])

        # try to update lot VAT
        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'],
                                                                                 self.tender_token),
                                       {'data': {'value': {'valueAddedTaxIncluded': True}}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [{u"location": u"body",
                                                    u"name": u"data",
                                                    u"description": u"Can't update lot for tender stage2"}])
        # but the value stays unchanged
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertTrue(lot['value']['valueAddedTaxIncluded'])

        # try to update minimalStep VAT
        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'],
                                                                                 self.tender_token),
                                       {"data": {"minimalStep": {"valueAddedTaxIncluded": True}}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [{u"location": u"body",
                                                    u"name": u"data",
                                                    u"description": u"Can't update lot for tender stage2"}])
        # but the value stays unchanged
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertTrue(lot['minimalStep']['valueAddedTaxIncluded'])

    def test_get_tender_lot(self):
        self.create_tender()
        response = self.app.get('/tenders/{}/lots'.format(self.tender_id))
        lot = response.json['data'][0]
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], 'active.tendering')

        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(set(response.json['data']), set([u'id', u'title', u'date', u'description', u'minimalStep', u'value', u'status', u'auctionPeriod']))

        self.set_status('active.qualification')

        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot.pop('auctionPeriod')
        res = response.json['data']
        res.pop('auctionPeriod')
        self.assertEqual(res, lot)

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
        self.create_tender()
        response = self.app.get('/tenders/{}/lots'.format(self.tender_id))
        lot = response.json['data'][0]

        response = self.app.get('/tenders/{}/lots'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(set(response.json['data'][0]), set([u'id',  u'date', u'title', u'description', u'minimalStep', u'value', u'status', u'auctionPeriod']))

        self.set_status('active.qualification')

        response = self.app.get('/tenders/{}/lots'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot.pop('auctionPeriod')
        res = response.json['data'][0]
        res.pop('auctionPeriod')
        self.assertEqual(res, lot,)

        response = self.app.get('/tenders/some_id/lots', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

    def test_delete_tender_lot(self):
        self.create_tender()
        response = self.app.get('/tenders/{}/lots'.format(self.tender_id))
        lot = response.json['data'][0]

        response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token),
                                   status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], "error")
        self.assertEqual(response.json['errors'], [{u'location': u'body',
                                                    u'name': u'data',
                                                    u'description': u'Can\'t delete lot for tender stage2'}])

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

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"items": [{'relatedLot': lot['id']}]}
                                        })
        self.assertEqual(response.status, '200 OK')

        response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token),
                                   status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [{u'location': u'body',
                                                    u'name': u'data',
                                                    u'description': u'Can\'t delete lot for tender stage2'}])
        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token),
                                   status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         u'Can\'t delete lot for tender stage2')

    def test_tender_lot_guarantee(self):
        lots = deepcopy(self.initial_lots)
        lots[0]['guarantee'] = {"amount": 20, "currency": "GBP"}
        self.create_tender(initial_lots=lots)
        lot = self.lots[0]
        lot_id = lot['id']
        response = self.app.get('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot_id, self.tender_token))
        self.assertEqual(response.json['data']['guarantee']['amount'], 20)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        lot = self.lots[1]
        lot_id = lot['id']
        response = self.app.get('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot_id, self.tender_token))
        self.assertNotIn('guarantee', response.json['data'])

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['guarantee']['amount'], 20)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

    def test_tender_lot_guarantee_v2(self):
        lots = deepcopy(self.initial_lots)
        lots[0]['guarantee'] = {"amount": 20, "currency": "GBP"}
        lots[1]['guarantee'] = {"amount": 40, "currency": "GBP"}
        self.create_tender(initial_lots=lots)
        lot = self.lots[0]
        lot_id = lot['id']
        response = self.app.get('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot_id, self.tender_token))
        self.assertEqual(response.json['data']['guarantee']['amount'], 20)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        lot = self.lots[1]
        lot_id = lot['id']
        response = self.app.get('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot_id, self.tender_token))
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 40)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['guarantee']['amount'], 60)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        lot2 = self.lots[1]
        lot2_id = lot2['id']
        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot2['id'],
                                                                                 self.tender_token),
                                       {'data': {'guarantee': {'amount': 50, 'currency': 'USD'}}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [{u"location": u"body",
                                                    u"name": u"data",
                                                    u"description": u"Can't update lot for tender stage2"}])

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 60)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                            {'data': {'guarantee': {'amount': 55}}})
        response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token))
        self.assertEqual(response.json['data']['guarantee']['amount'], 60)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                            {'data': {'guarantee': {"amount": 35, "currency": "GBP"}}})

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 60)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        for l_id in (lot_id, lot2_id):
            response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                                     l_id,
                                                                                     self.tender_token),
                                           {'data': {'guarantee': {"amount": 0, "currency": "GBP"}}},
                                           status=403)
            self.assertEqual(response.status, '403 Forbidden')
            self.assertEqual(response.json['errors'], [{u"location": u"body",
                                                        u"name": u"data",
                                                        u"description": u"Can't update lot for tender stage2"}])
            response = self.app.get('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, l_id, self.tender_token))
            self.assertNotEqual(response.json['data']['guarantee']['amount'], 0)
            self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 60)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")


class TenderStage2LotEdgeCasesMixin(object):
    expected_status = None

    def test_question_blocking(self):
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'lot',
                                                'relatedItem': self.lots[0]['id'],
                                                'author': self.initial_bids[0]['tenderers'][0]}})
        question = response.json['data']
        self.assertEqual(question['questionOf'], 'lot')
        self.assertEqual(question['relatedItem'], self.lots[0]['id'])

        self.set_status(self.expected_status, extra={"status": "active.tendering"})
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
                                                "relatedLot": self.lots[0]['id']}})

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], self.expected_status)

    def test_claim_blocking(self):
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id),
                                      {'data': {'title': 'complaint title',
                                                'description': 'complaint description',
                                                'author': self.initial_bids[0]['tenderers'][0],
                                                'relatedLot': self.lots[0]['id'],
                                                'status': 'claim'}})
        self.assertEqual(response.status, '201 Created')
        complaint = response.json['data']
        self.assertEqual(complaint['relatedLot'], self.lots[0]['id'])

        self.set_status(self.expected_status, extra={"status": "active.tendering"})
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
                                                "relatedLot": self.lots[0]['id']}})

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})

        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], self.expected_status)

    def test_next_check_value_with_unanswered_question(self):
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id),
                                      {'data': {'title': 'question title',
                                                'description': 'question description',
                                                'questionOf': 'lot',
                                                'relatedItem': self.lots[0]['id'],
                                                'author': self.initial_bids[0]['tenderers'][0]}})
        question = response.json['data']
        self.assertEqual(question['questionOf'], 'lot')
        self.assertEqual(question['relatedItem'], self.lots[0]['id'])

        self.set_status(self.expected_status, extra={"status": "active.tendering"})
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
                                                "relatedLot": self.lots[0]['id']}})

        response = self.app.get('/tenders/{}'.format(self.tender_id, ))
        self.assertIn('next_check', response.json['data'])
        self.assertEqual(response.json['data']['next_check'], response.json['data']['tenderPeriod']['endDate'])

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], self.expected_status)

    def test_next_check_value_with_unanswered_claim(self):
        response = self.app.post_json('/tenders/{}/complaints'.format(self.tender_id),
                                      {'data': {'title': 'complaint title',
                                                'description': 'complaint description',
                                                'author': self.initial_bids[0]['tenderers'][0],
                                                'relatedLot': self.lots[0]['id'],
                                                'status': 'claim'}})
        self.assertEqual(response.status, '201 Created')
        complaint = response.json['data']
        self.assertEqual(complaint['relatedLot'], self.lots[0]['id'])

        self.set_status(self.expected_status, extra={"status": "active.tendering"})

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
                                                "relatedLot": self.lots[0]['id']}})

        response = self.app.get('/tenders/{}'.format(self.tender_id, ))
        self.assertIn('next_check', response.json['data'])
        self.assertEqual(response.json['data']['next_check'], response.json['data']['tenderPeriod']['endDate'])

        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], self.expected_status)


class TenderStage2EULotEdgeCasesTest(BaseCompetitiveDialogEUStage2ContentWebTest, TenderStage2LotEdgeCasesMixin):
    initial_auth = ('Basic', ('broker', ''))
    initial_lots = [deepcopy(test_lots[0]) for i in range(2)]
    expected_status = "active.pre-qualification"

    def setUp(self):
        s2_bids = [deepcopy(bid) for bid in test_bids]
        for bid in s2_bids:
            # bid['tenderers'][0]['identifier']['id'] = '00000{}'.format(n)
            bid['tenderers'][0]['identifier']['id'] = self.initial_data['shortlistedFirms'][0]['identifier']['id']
            bid['tenderers'][0]['identifier']['scheme'] = self.initial_data['shortlistedFirms'][0]['identifier']['scheme']
        self.initial_bids = s2_bids
        super(TenderStage2EULotEdgeCasesTest, self).setUp()


class TenderStage2EULotFeatureResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):

    initial_lots = [deepcopy(test_lots[0]) for i in range(3)]
    initial_auth = ('Basic', ('broker', ''))

    def test_tender_value(self):
        request_path = '/tenders/{}'.format(self.tender_id)
        response = self.app.get(request_path)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['value']['amount'], sum([i['value']['amount'] for i in self.lots]))
        self.assertEqual(response.json['data']['minimalStep']['amount'], min([i['minimalStep']['amount'] for i in self.lots]))

    def test_tender_features_invalid(self):
        request_path = '/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token)
        data = test_tender_data.copy()
        item = data['items'][0].copy()
        item['id'] = "1"
        data['items'] = [item]
        data['features'] = [
            {
                "featureOf": "lot",
                "relatedItem": self.lots[0]['id'],
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
        data['features'][0]["enum"][0]["value"] = 0.1
        data['features'].append(data['features'][0].copy())
        data['features'].append(data['features'][0].copy())
        data['features'].append(data['features'][0].copy())
        data['features'][1]["enum"][0]["value"] = 0.2
        data['features'][2]["enum"][0]["value"] = 0.3
        data['features'][3]["enum"][0]["value"] = 0.3
        response = self.app.patch_json(request_path, {'data': data}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'Sum of max value of all features for lot should be less then or equal to 99%'],
             u'location': u'body',
             u'name': u'features'}
        ])
        data['features'][1]["enum"][0]["value"] = 0.1
        data['features'].append(data['features'][0].copy())
        data['features'][2]["relatedItem"] = self.lots[1]['id']
        data['features'].append(data['features'][2].copy())
        response = self.app.patch_json(request_path, {'data': data})
        self.assertEqual(response.status, '200 OK')


class TenderStage2EULotBidderResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):

    initial_lots = deepcopy(test_lots)
    initial_auth = ('Basic', ('broker', ''))

    def test_create_tender_bidder_invalid(self):
        request_path = '/tenders/{}/bids'.format(self.tender_id)
        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': test_bids[0]['tenderers']}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'lotValues'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': test_bids[0]['tenderers'], 'lotValues': [{"value": {"amount": 500}}]}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'relatedLot': [u'This field is required.']}], u'location': u'body', u'name': u'lotValues'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': test_bids[0]['tenderers'], 'lotValues': [{"value": {"amount": 500}, 'relatedLot': "0" * 32}]}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'relatedLot': [u'relatedLot should be one of lots']}], u'location': u'body', u'name': u'lotValues'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': test_bids[0]['tenderers'], 'lotValues': [{"value": {"amount": 5000000}, 'relatedLot': self.lots[0]['id']}]}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'value': [u'value of bid should be less than value of lot']}], u'location': u'body', u'name': u'lotValues'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': test_bids[0]['tenderers'], 'lotValues': [{"value": {"amount": 500, 'valueAddedTaxIncluded': False}, 'relatedLot': self.lots[0]['id']}]}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'value': [u'valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of lot']}], u'location': u'body', u'name': u'lotValues'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': test_bids[0]['tenderers'], 'lotValues': [{"value": {"amount": 500, 'currency': "USD"}, 'relatedLot': self.lots[0]['id']}]}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'value': [u'currency of bid should be identical to currency of value of lot']}], u'location': u'body', u'name': u'lotValues'},
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True, 'tenderers': test_bids[0]['tenderers'], "value": {"amount": 500}, 'lotValues': [{"value": {"amount": 500}, 'relatedLot': self.lots[0]['id']}]}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'value should be posted for each lot of bid'], u'location': u'body', u'name': u'value'}
        ])

    def test_patch_tender_bidder(self):
        lot_id = self.lots[0]['id']
        tenderers = deepcopy(test_bids[0]["tenderers"])
        tenderers[0]['identifier']['id'] = self.initial_data['shortlistedFirms'][0]['identifier']['id']
        tenderers[0]['identifier']['scheme'] = self.initial_data['shortlistedFirms'][0]['identifier']['scheme']
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True,
                                                'selfQualified': True,
                                                'tenderers': tenderers,
                                                'lotValues': [{'value': {'amount': 500},
                                                               'relatedLot': lot_id}]}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bidder = response.json['data']
        bid_token = response.json['access']['token']
        lot = bidder['lotValues'][0]

        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bidder['id'],
                                                                                 bid_token),
                                       {u'data': {u'tenderers': [{
                                           u'name': u'Державне управління управлінням справами'}]
                                       }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lotValues'][0]['date'], lot['date'])
        self.assertNotEqual(response.json['data']['tenderers'][0]['name'], bidder['tenderers'][0]['name'])

        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bidder['id'],
                                                                                 bid_token),
                                       {"data": {'lotValues': [{'value': {"amount": 500},
                                                 'relatedLot': lot_id}],
                                                 'tenderers': test_bids[0]['tenderers']}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lotValues'][0]['date'], lot['date'])
        self.assertEqual(response.json['data']['tenderers'][0]['name'], bidder['tenderers'][0]['name'])

        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bidder['id'],
                                                                                 bid_token),
                                       {"data": {'lotValues': [{"value": {"amount": 400}, 'relatedLot': lot_id}]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lotValues'][0]["value"]["amount"], 400)
        self.assertNotEqual(response.json['data']['lotValues'][0]['date'], lot['date'])

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


class TenderStage2EULotFeatureBidderResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_lots = deepcopy(test_lots)
    initial_auth = ('Basic', ('broker', ''))
    initial_features = [
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
            "relatedItem": "3",
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

    def __init__(self, *args, **kwargs):
        self.id_first_lot = uuid4().hex
        self.id_first_item = uuid4().hex
        self.initial_lots[0]['id'] = self.id_first_lot
        self.initial_data = deepcopy(self.initial_data)
        self.initial_data['items'][0]['id'] = self.id_first_item
        self.initial_features[0]['relatedItem'] = self.id_first_lot
        self.initial_features[1]['relatedItem'] = self.id_first_item
        super(TenderStage2EULotFeatureBidderResourceTest, self).__init__(*args, **kwargs)

    def setUp(self):
        super(TenderStage2EULotFeatureBidderResourceTest, self).setUp()
        self.app.authorization = ('Basic', ('broker', ''))
        self.lot_id = self.initial_lots[0]['id']
        self.create_tender(initial_lots=self.initial_lots, features=self.initial_features)

    def test_create_tender_bidder_invalid(self):
        tenderers = deepcopy(test_bids[0]["tenderers"])
        tenderers[0]['identifier']['id'] = self.initial_data['shortlistedFirms'][0]['identifier']['id']
        tenderers[0]['identifier']['scheme'] = self.initial_data['shortlistedFirms'][0]['identifier']['scheme']

        request_path = '/tenders/{}/bids'.format(self.tender_id)
        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': tenderers}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')

        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': tenderers,
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
                                                              'tenderers': tenderers,
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

        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': tenderers,
                                                              'lotValues': [{"value": {"amount": 5000000},
                                                                             'relatedLot': self.lot_id}]}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'value': [u'value of bid should be less than value of lot']}],
             u'location': u'body', u'name': u'lotValues'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': tenderers,
                                                              'lotValues': [{"value": {"amount": 500,
                                                                                       'valueAddedTaxIncluded': False},
                                                                             'relatedLot': self.lot_id}]}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'value': [u'valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of lot']}],
             u'location': u'body', u'name': u'lotValues'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': tenderers,
                                                              'lotValues': [{"value": {"amount": 500,
                                                                                       'currency': "USD"},
                                                                             'relatedLot': self.lot_id}]}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'value': [u'currency of bid should be identical to currency of value of lot']}],
             u'location': u'body', u'name': u'lotValues'},
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': tenderers,
                                                              'lotValues': [{"value": {"amount": 500},
                                                                             'relatedLot': self.lot_id}]}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')

        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': tenderers,
                                                              'lotValues': [{"value": {"amount": 500},
                                                                             'relatedLot': self.lot_id}]}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'All features parameters is required.'], u'location': u'body', u'name': u'parameters'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': tenderers,
                                                              'lotValues': [{"value": {"amount": 500},
                                                                             'relatedLot': self.lot_id}],
                                                              'parameters': [{"code": "code_item", "value": 0.01}]}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'All features parameters is required.'], u'location': u'body', u'name': u'parameters'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': tenderers,
                                                              'lotValues': [{"value": {"amount": 500},
                                                                             'relatedLot': self.lot_id}],
                                                              'parameters': [{"code": "code_invalid",
                                                                              "value": 0.01}]}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'code': [u'code should be one of feature code.']}], u'location': u'body',
             u'name': u'parameters'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': tenderers,
                                                              'lotValues': [{"value": {"amount": 500},
                                                                             'relatedLot': self.lot_id}],
                                                              'parameters': [{"code": "code_item", "value": 0.01},
                                                                             {"code": "code_tenderer", "value": 0},
                                                                             {"code": "code_lot", "value": 0.01}]}
                                                     },
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'value': [u'value should be one of feature value.']}], u'location': u'body',
             u'name': u'parameters'}
        ])

    def test_create_tender_bidder(self):
        tenderers = deepcopy(test_bids[0]["tenderers"])
        tenderers[0]['identifier']['id'] = self.initial_data['shortlistedFirms'][0]['identifier']['id']
        tenderers[0]['identifier']['scheme'] = self.initial_data['shortlistedFirms'][0]['identifier']['scheme']

        request_path = '/tenders/{}/bids'.format(self.tender_id)
        response = self.app.post_json(request_path, {'data': {'selfEligible': True,
                                                              'selfQualified': True,
                                                              'tenderers': tenderers,
                                                              'lotValues': [{"value": {"amount": 500},
                                                                             'relatedLot': self.lot_id}],
                                                              'parameters': [{"code": "code_item", "value": 0.01},
                                                                             {"code": "code_tenderer", "value": 0.01},
                                                                             {"code": "code_lot", "value": 0.01}]}
                                                     })
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bidder = response.json['data']
        self.assertEqual(bidder['tenderers'][0]['name'], test_tender_data["procuringEntity"]['name'])
        self.assertIn('id', bidder)
        self.assertIn(bidder['id'], response.headers['Location'])

        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': tenderers,
                                                              'lotValues': [{"value": {"amount": 500},
                                                                             'relatedLot': self.lot_id}],
                                                              'parameters': [{"code": "code_item", "value": 0.01},
                                                                             {"code": "code_tenderer", "value": 0.01},
                                                                             {"code": "code_lot", "value": 0.01}]}
                                                     },
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add bid in current (unsuccessful) tender status")


class TenderStage2EULotProcessTest(BaseCompetitiveDialogEUWebTest):

    initial_data = test_tender_stage2_data_eu

    def setUp(self):
        super(TenderStage2EULotProcessTest, self).setUp()
        self.app.authorization = ('Basic', ('broker', ''))

    def create_tenderers(self, count=1):
        tenderers = []
        for i in xrange(count):
            tenderer = deepcopy(test_bids[0]["tenderers"])
            tenderer[0]['identifier']['id'] = self.initial_data['shortlistedFirms'][i if i < 3 else 3]['identifier']['id']
            tenderer[0]['identifier']['scheme'] = self.initial_data['shortlistedFirms'][i if i < 3 else 3]['identifier']['scheme']
            tenderers.append(tenderer)
        return tenderers

    def create_tender(self, initial_lots, features=None):
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))
        data = deepcopy(self.initial_data)
        if initial_lots:
            lots = []
            for i in initial_lots:
                lot = deepcopy(i)
                if 'id' not in lot:
                    lot['id'] = uuid4().hex
                lots.append(lot)
            data['lots'] = self.initial_lots = lots
            for i, item in enumerate(data['items']):
                item['relatedLot'] = lots[i % len(lots)]['id']
            for firm in data['shortlistedFirms']:
                firm['lots'] = [dict(id=lot['id']) for lot in lots]
            self.lots_id = [lot['id'] for lot in lots]
        if features:
            for feature in features:
                if feature['featureOf'] == 'lot':
                    feature['relatedItem'] = data['lots'][0]['id']
                if feature['featureOf'] == 'item':
                    feature['relatedItem'] = data['items'][0]['id']
            data['features'] = self.features = features
        response = self.app.post_json('/tenders', {'data': data})
        tender = response.json['data']
        self.tender = tender
        self.tender_token = response.json['access']['token']
        self.tender_id = tender['id']
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))
        self.app.patch_json('/tenders/{id}?acc_token={token}'.format(id=self.tender_id,
                                                                     token=self.tender_token),
                            {'data': {'status': 'draft.stage2'}})

        self.app.authorization = ('Basic', ('broker', ''))
        self.app.patch_json('/tenders/{id}?acc_token={token}'.format(id=self.tender_id,
                                                                     token=self.tender_token),
                            {'data': {'status': 'active.tendering'}})
        self.app.authorization = auth

    def test_1lot_0bid(self):
        self.create_tender(test_lots)
        response = self.set_status('active.tendering', {"lots": [{"auctionPeriod": {"startDate": (get_now() + timedelta(days=10)).isoformat()}}]})
        self.assertIn("auctionPeriod", response.json['data']['lots'][0])
        # switch to unsuccessful
        self.set_status('active.pre-qualification', {'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']["lots"][0]['status'], 'unsuccessful')
        self.assertEqual(response.json['data']['status'], 'unsuccessful')

        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [{
            "location": "body", "name": "data", "description": "Can't create lot for tender stage2"
        }])

    def test_1lot_1bid(self):
        self.create_tender(test_lots)
        tenderers = deepcopy(test_bids[0]["tenderers"])
        tenderers[0]['identifier']['id'] = self.initial_data['shortlistedFirms'][0]['identifier']['id']
        tenderers[0]['identifier']['scheme'] = self.initial_data['shortlistedFirms'][0]['identifier']['scheme']
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                                'tenderers': tenderers,
                                                'lotValues': [{"value": {"amount": 500},
                                                               'relatedLot': self.initial_lots[0]['id']}]}})
        # switch to active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.check_chronograph()
        # switch to unsuccessful
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token))
        self.assertEqual(response.json['data']['status'], 'unsuccessful')

    def test_1lot_2bid_1unqualified(self):
        self.create_tender(test_lots)
        tenderers = deepcopy(test_bids[0]["tenderers"])
        tenderers[0]['identifier']['id'] = self.initial_data['shortlistedFirms'][0]['identifier']['id']
        tenderers[0]['identifier']['scheme'] = self.initial_data['shortlistedFirms'][0]['identifier']['scheme']
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                                'tenderers': tenderers,
                                                'lotValues': [{"value": {"amount": 500},
                                                               'relatedLot': self.initial_lots[0]['id']}]}})

        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                                'tenderers': tenderers,
                                                'lotValues': [{"value": {"amount": 500},
                                                               'relatedLot': self.initial_lots[0]['id']}]}})
        # switch to active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, self.tender_token))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']

        response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                           qualifications[0]['id'],
                                                                                           self.tender_token),
                                  {"data": {'status': 'active', "qualified": True, "eligible": True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active')

        response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                           qualifications[1]['id'],
                                                                                           self.tender_token),
                                  {"data": {'status': 'unsuccessful'}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'unsuccessful')
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "active.pre-qualification.stand-still")

        self.set_status('active.auction', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json['data']['status'], "unsuccessful")

    def test_1lot_2bid(self):
        # create tender with item and lot
        self.create_tender(initial_lots=test_lots)
        tenderers_1 = deepcopy(test_bids[0]["tenderers"])
        tenderers_1[0]['identifier']['id'] = self.initial_data['shortlistedFirms'][0]['identifier']['id']
        tenderers_1[0]['identifier']['scheme'] = self.initial_data['shortlistedFirms'][0]['identifier']['scheme']
        tenderers_2 = deepcopy(test_bids[1]["tenderers"])
        tenderers_2[0]['identifier']['id'] = self.initial_data['shortlistedFirms'][1]['identifier']['id']
        tenderers_2[0]['identifier']['scheme'] = self.initial_data['shortlistedFirms'][1]['identifier']['scheme']
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                                'tenderers': tenderers_1,
                                                'lotValues': [{"value": {"amount": 450},
                                                               'relatedLot': self.lots_id[0]}]}})
        bid_id = response.json['data']['id']
        bid_token = response.json['access']['token']
        # create second bid
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                           {'data': {'selfEligible': True, 'selfQualified': True,
                                     'tenderers': tenderers_2,
                                     'lotValues': [{"value": {"amount": 475},
                                                    'relatedLot': self.lots_id[0]}]}})
        # switch to active.auction
        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, self.tender_token))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']
        for qualification in qualifications:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                               qualification['id'],
                                                                                               self.tender_token),
                                      {"data": {'status': 'active', "qualified": True, "eligible": True}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active')

        response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token))
        self.assertEqual(response.status, '200 OK')

        for bid in response.json['data']['bids']:
            self.assertEqual(bid['status'], 'active')

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")
        self.check_chronograph()

        response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token))
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.status, "200 OK")

        self.time_shift('active.auction')

        self.check_chronograph()

        # get auction info
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        # posting auction urls
        response = self.app.patch_json('/tenders/{}/auction/{}'.format(self.tender_id, self.lots_id[0]), {
            'data': {
                'lots': [
                    {
                        'id': i['id'],
                        'auctionUrl': 'https://tender.auction.url'
                    }
                    for i in response.json['data']['lots']
                ],
                'bids': [
                    {
                        'id': i['id'],
                        'lotValues': [
                            {
                                'relatedLot': j['relatedLot'],
                                'participationUrl': 'https://tender.auction.url/for_bid/{}'.format(i['id'])
                            }
                            for j in i['lotValues']
                        ],
                    }
                    for i in auction_bids_data
                ]
            }
        })
        # view bid participationUrl
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid_id, bid_token))
        self.assertEqual(response.json['data']['lotValues'][0]['participationUrl'], 'https://tender.auction.url/for_bid/{}'.format(bid_id))
        # posting auction results
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, self.lots_id[0]),
                                      {'data': {'bids': auction_bids_data}})
        # # get awards
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.tender_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
        # set award as active
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                            {"data": {"status": "active", "qualified": True, "eligible": True}})
        # get contract id
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        contract_id = response.json['data']['contracts'][-1]['id']
        # after stand still period

        self.time_shift('complete')
        self.check_chronograph()

        # # time travel
        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)
        # # sign contract
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, contract_id,
                                                                           self.tender_token),
                            {"data": {"status": "active"}})
        # check status
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['lots'][0]['status'], 'complete')
        self.assertEqual(response.json['data']['status'], 'complete')

    def test_2lot_2bid_1lot_del(self):
        # create tender 2 lot
        self.create_tender(initial_lots=test_lots * 2)
        self.app.authorization = ('Basic', ('broker', ''))

        self.set_status('active.tendering',
                        {"lots": [{"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}
                                  for i in self.initial_lots]}
                        )
        # create bid
        tenderers_1 = deepcopy(test_bids[0]["tenderers"])
        tenderers_1[0]['identifier']['id'] = self.initial_data['shortlistedFirms'][0]['identifier']['id']
        tenderers_1[0]['identifier']['scheme'] = self.initial_data['shortlistedFirms'][0]['identifier']['scheme']
        tenderers_2 = deepcopy(test_bids[1]["tenderers"])
        tenderers_2[0]['identifier']['id'] = self.initial_data['shortlistedFirms'][1]['identifier']['id']
        tenderers_2[0]['identifier']['scheme'] = self.initial_data['shortlistedFirms'][1]['identifier']['scheme']

        bids = []
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                                'tenderers': tenderers_1,
                                                'lotValues': [{"value": {"amount": 500}, 'relatedLot': lot['id']}
                                                              for lot in self.initial_lots]
                                                }
                                       })
        bids.append(response.json)
        # create second bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                                'tenderers': tenderers_2,
                                                'lotValues': [{"value": {"amount": 500}, 'relatedLot': lot['id']}
                                                              for lot in self.initial_lots]}
                                       })
        bids.append(response.json)
        response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, self.initial_lots[0]['id'],
                                                                             self.tender_token),
                                   status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], "Can't delete lot for tender stage2")

    def test_1lot_3bid_1del(self):
        """ Create tender with 1 lot and 3 bids, later delete 1 bid """
        self.create_tender(initial_lots=test_lots)
        tenderers = []
        for i in xrange(3):
            tenderer = deepcopy(test_bids[0]["tenderers"])
            tenderer[0]['identifier']['id'] = self.initial_data['shortlistedFirms'][i]['identifier']['id']
            tenderer[0]['identifier']['scheme'] = self.initial_data['shortlistedFirms'][i]['identifier']['scheme']
            tenderers.append(tenderer)
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        bids = []
        for i in range(3):
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                          {'data': {'selfEligible': True, 'selfQualified': True,
                                                    'tenderers': tenderers[i],
                                                    'lotValues': [{'value': {'amount': 450},
                                                                   'relatedLot': self.initial_lots[0]['id']}]}})
            bids.append({response.json['data']['id']: response.json['access']['token']})

        response = self.app.delete('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id,
                                                                             bids[2].keys()[0],
                                                                             bids[2].values()[0]),
                                   status=200)
        self.assertEqual(response.status, '200 OK')
        # switch to active.auction
        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, self.tender_token))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']

        for qualification in qualifications:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualification['id'], self.tender_token),
                                      {"data": {'status': 'active', "qualified": True, "eligible": True}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active')
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")
        self.check_chronograph()

        response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token))
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.status, "200 OK")

        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, self.tender_token))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']

        self.time_shift('active.auction')

        self.check_chronograph()
        # get auction info
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        # posting auction urls
        data ={
            'data': {
                'lots': [
                    {
                        'id': i['id'],
                        'auctionUrl': 'https://tender.auction.url'
                    }
                    for i in response.json['data']['lots']
                ],
                'bids': list(auction_bids_data)
            }
        }

        for bid_index, bid in enumerate(auction_bids_data):
            if bid.get('status', 'active') == 'active':
                for lot_index, lot_bid in enumerate(bid['lotValues']):
                    if lot_bid['relatedLot'] == self.initial_lots[0]['id'] and \
                            lot_bid.get('status', 'active') == 'active':
                        data['data']['bids'][bid_index]['lotValues'][lot_index]['participationUrl'] = 'https://tender.auction.url/for_bid/{}'.format(bid['id'])
                        break

        response = self.app.patch_json('/tenders/{}/auction/{}'.format(self.tender_id, self.initial_lots[0]['id']), data)
        # view bid participationUrl
        self.app.authorization = ('Basic', ('broker', ''))
        bid_id = bids[0].keys()[0]
        bid_token = bids[0].values()[0]
        response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid_id, bid_token))
        self.assertEqual(response.json['data']['lotValues'][0]['participationUrl'],
                         'https://tender.auction.url/for_bid/{}'.format(bid_id))

        bid_id = bids[2].keys()[0]
        bid_token = bids[2].values()[0]
        response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid_id, bid_token))
        self.assertEqual(response.json['data']['status'], 'deleted')

        # posting auction results
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, self.initial_lots[0]['id']),
                                      {'data': {'bids': auction_bids_data}})
        # # get awards
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.tender_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
        # set award as active
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                            {"data": {"status": "active", "qualified": True, "eligible": True}})
        # get contract id
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        contract_id = response.json['data']['contracts'][-1]['id']
        # after stand still period

        self.time_shift('complete')
        self.check_chronograph()

        # # time travel
        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)
        # # sign contract
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id,
                                                                           contract_id,
                                                                           self.tender_token),
                            {"data": {"status": "active"}})
        # check status
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']["lots"][0]['status'], 'complete')
        self.assertEqual(response.json['data']['status'], 'complete')

    def test_1lot_3bid_1un(self):
        """ Create tender with 1 lot and 3 bids, later 1 bid unsuccessful"""
        self.create_tender(initial_lots=test_lots)
        bid_count = 3
        tenderers = self.create_tenderers(bid_count)
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        bids = []
        for i in xrange(bid_count):
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                          {'data': {'selfEligible': True, 'selfQualified': True,
                                                    'tenderers': tenderers[i],
                                                    'lotValues': [{'value': {"amount": 450},
                                                                   'relatedLot': self.initial_lots[0]['id']}]
                                                    }
                                           })
            bids.append({response.json['data']['id']: response.json['access']['token']})

        # switch to active.auction
        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, self.tender_token))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']
        for qualification in qualifications:
            if qualification['bidID'] == bids[2].keys()[0]:
                response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                                   qualification['id'],
                                                                                                   self.tender_token),
                                          {"data": {'status': 'unsuccessful'}})
                self.assertEqual(response.status, '200 OK')
                self.assertEqual(response.json['data']['status'], 'unsuccessful')
            else:
                response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                                   qualification['id'],
                                                                                                   self.tender_token),
                                               {'data': {'status': 'active', "qualified": True, "eligible": True}})
                self.assertEqual(response.status, '200 OK')
                self.assertEqual(response.json['data']['status'], 'active')
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id,
                                                                         self.tender_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")
        self.check_chronograph()

        response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id,
                                                                  self.tender_token))
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.status, "200 OK")

        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id,
                                                                                 self.tender_token))
        self.assertEqual(response.content_type, 'application/json')

        self.time_shift('active.auction')

        self.check_chronograph()
        # get auction info
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        # posting auction urls
        data ={
            'data': {
                'lots': [
                    {
                        'id': i['id'],
                        'auctionUrl': 'https://tender.auction.url'
                    }
                    for i in response.json['data']['lots']
                ],
                'bids': list(auction_bids_data)
            }
        }

        for bid_index, bid in enumerate(auction_bids_data):
            if bid.get('status', 'active') == 'active':
                for lot_index, lot_bid in enumerate(bid['lotValues']):
                    if lot_bid['relatedLot'] == self.initial_lots[0]['id'] and lot_bid.get('status', 'active') == 'active':
                        data['data']['bids'][bid_index]['lotValues'][lot_index]['participationUrl'] = 'https://tender.auction.url/for_bid/{}'.format(bid['id'])
                        break

        response = self.app.patch_json('/tenders/{}/auction/{}'.format(self.tender_id,
                                                                       self.initial_lots[0]['id']),
                                       data)
        # view bid participationUrl
        self.app.authorization = ('Basic', ('broker', ''))
        bid_id = bids[0].keys()[0]
        bid_token = bids[0].values()[0]
        response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid_id, bid_token))
        self.assertEqual(response.json['data']['lotValues'][0]['participationUrl'],
                         'https://tender.auction.url/for_bid/{}'.format(bid_id))

        bid_id = bids[2].keys()[0]
        bid_token = bids[2].values()[0]
        response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid_id, bid_token))
        self.assertNotIn('lotValues', response.json['data'])

        # posting auction results
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, self.initial_lots[0]['id']),
                                      {'data': {'bids': auction_bids_data}})
        # # get awards
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.tender_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
        # set award as active
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                            {"data": {"status": "active", "qualified": True, "eligible": True}})
        # get contract id
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        contract_id = response.json['data']['contracts'][-1]['id']
        # after stand still period

        self.time_shift('complete')
        self.check_chronograph()

        # # time travel
        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)
        # # sign contract
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id,
                                                                           contract_id,
                                                                           self.tender_token),
                            {"data": {"status": "active"}})
        # check status
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']["lots"][0]['status'], 'complete')
        self.assertEqual(response.json['data']['status'], 'complete')

    def test_2lot_0bid(self):
        """ Create tender with 2 lots and 0 bids """
        self.create_tender(initial_lots=test_lots*2)

        self.time_shift('active.pre-qualification')
        self.check_chronograph()
        # switch to unsuccessful
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token))
        self.assertTrue(all([i['status'] == 'unsuccessful' for i in response.json['data']['lots']]))
        self.assertEqual(response.json['data']['status'], 'unsuccessful')

    def test_2lot_2can(self):
        """ Create tender with 2 lots, later cancel both """
        self.create_tender(test_lots*2)
        # cancel every lot
        for lot in self.initial_lots:
            self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
                                {'data': {'reason': 'cancellation reason',
                                          'status': 'active',
                                          'cancellationOf': 'lot',
                                          'relatedLot': lot['id']}
                                 })
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertTrue(all([i['status'] == 'cancelled' for i in response.json['data']['lots']]))
        self.assertEqual(response.json['data']['status'], 'cancelled')

    def test_2lot_1can(self):
        """ Create tender with 2 lots, later 1 cancel """
        self.create_tender(initial_lots=test_lots * 2)
        # cancel first lot
        self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
                           {'data': {
                               'reason': 'cancellation reason',
                               'status': 'active',
                               'cancellationOf': 'lot',
                               'relatedLot': self.initial_lots[0]['id']}
                           })

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertFalse(all([i['status'] == 'cancelled' for i in response.json['data']['lots']]))
        self.assertTrue(any([i['status'] == 'cancelled' for i in response.json['data']['lots']]))
        self.assertEqual(response.json['data']['status'], 'active.tendering')

        # try to restore lot back by old cancellation
        response = self.app.get('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token))
        self.assertEqual(len(response.json['data']), 1)
        cancellation = response.json['data'][0]
        self.assertEqual(cancellation['status'], 'active')

        response = self.app.patch_json('/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id,
                                                                                          cancellation['id'],
                                                                                          self.tender_token),
                                       {'data': {'status': 'pending'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'][0]["description"], "Can update cancellation only in active lot status")

        # try to restore lot back by new pending cancellation
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                      self.tender_token),
                                      {'data': {'reason': 'cancellation reason',
                                                'status': 'pending',
                                                'cancellationOf': 'lot',
                                                'relatedLot': self.initial_lots[0]['id']}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'][0]["description"], "Can add cancellation only in active lot status")
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertFalse(all([i['status'] == 'cancelled' for i in response.json['data']['lots']]))
        self.assertTrue(any([i['status'] == 'cancelled' for i in response.json['data']['lots']]))
        self.assertEqual(response.json['data']['status'], 'active.tendering')

    def test_2lot_2bid_0com_1can(self):
        """ Create tender with 2 lots and 2 bids """
        self.create_tender(test_lots*2)
        tenderers = self.create_tenderers(2)
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                           {'data': {'selfEligible': True, 'selfQualified': True,
                                     'tenderers': tenderers[0], 'lotValues': [{'value': {'amount': 500},
                                                                               'relatedLot': lot['id']}
                                                                              for lot in self.initial_lots]}
                            })

        self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                           {'data': {'selfEligible': True, 'selfQualified': True,
                                     'tenderers': tenderers[1], 'lotValues': [{'value': {'amount': 499},
                                                                               'relatedLot': lot['id']}
                                                                              for lot in self.initial_lots]
                                     }
                            })

        self.app.authorization = ('Basic', ('broker', ''))
        self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, self.tender_token),
                           {'data': {'reason': 'cancellation reason',
                                     'status': 'active',
                                     "cancellationOf": "lot",
                                     "relatedLot": self.initial_lots[0]['id']}
                            })
        response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token))
        self.assertEqual(response.status, "200 OK")
        # active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.check_chronograph()

        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, self.tender_token))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']
        self.assertEqual(len(qualifications), 2)

        for qualification in qualifications:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                               qualification['id'],
                                                                                               self.tender_token),
                                      {"data": {'status': 'active', "qualified": True, "eligible": True}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active')
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")

    def test_2lot_2bid_2com_2win(self):
        """ Create tender with 2 lots and 2 bids """
        self.create_tender(initial_lots=test_lots*2)
        tenderers = self.create_tenderers(2)
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                           {'data': {'selfEligible': True,
                                     'selfQualified': True,
                                     'tenderers': tenderers[0],
                                     'lotValues': [{"value": {"amount": 500}, 'relatedLot': lot['id']}
                                                   for lot in self.initial_lots]}
                            })
        # create second bid
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                           {'data': {'selfEligible': True,
                                     'selfQualified': True,
                                     'tenderers': tenderers[1],
                                     'lotValues': [{"value": {"amount": 500}, 'relatedLot': lot['id']}
                                                   for lot in self.initial_lots]}
                            })
        # switch to active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.check_chronograph()
        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, self.tender_token))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']
        self.assertEqual(len(qualifications), 4)

        for qualification in qualifications:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id,
                                                                                               qualification['id'],
                                                                                               self.tender_token),
                                      {"data": {'status': 'active', "qualified": True, "eligible": True}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active')
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"status": "active.pre-qualification.stand-still"}})
        self.assertEqual(response.status, "200 OK")
        # switch to active.auction
        self.time_shift('active.auction')
        self.check_chronograph()
        # get auction info
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        for lot in self.initial_lots:
            # posting auction urls
            self.app.patch_json('/tenders/{}/auction/{}'.format(self.tender_id, lot['id']), {
                'data': {
                    'lots': [
                        {
                            'id': i['id'],
                            'auctionUrl': 'https://tender.auction.url'
                        }
                        for i in response.json['data']['lots']
                    ],
                    'bids': [
                        {
                            'id': i['id'],
                            'lotValues': [
                                {
                                    'relatedLot': j['relatedLot'],
                                    'participationUrl': 'https://tender.auction.url/for_bid/{}'.format(i['id'])
                                }
                                for j in i['lotValues']
                            ],
                        }
                        for i in auction_bids_data
                    ]
                }
            })
            # posting auction results
            self.app.authorization = ('Basic', ('auction', ''))
            response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot['id']),
                                          {'data': {'bids': auction_bids_data}})
        # for first lot
        lot_id = self.initial_lots[0]['id']
        # get awards
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.tender_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == lot_id][0]
        # set award as active
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                            {"data": {"status": "active", "qualified": True, "eligible": True}})
        # get contract id
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        contract_id = response.json['data']['contracts'][-1]['id']
        # after stand slill period
        self.set_status('complete', {'status': 'active.awarded'})
        # time travel
        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)
        # sign contract
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id,
                                                                           contract_id,
                                                                           self.tender_token),
                            {"data": {"status": "active"}})
        # for second lot
        lot_id = self.initial_lots[1]['id']
        # get awards
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.tender_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == lot_id][0]
        # set award as unsuccessful
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                            {"data": {"status": "unsuccessful"}})
        # get awards
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.tender_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == lot_id][0]
        # set award as active
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                            {"data": {"status": "active", "qualified": True, "eligible": True}})
        # get contract id
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        contract_id = response.json['data']['contracts'][-1]['id']
        # after stand still period
        self.set_status('complete', {'status': 'active.awarded'})
        # time travel
        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)
        # sign contract
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id,
                                                                           contract_id,
                                                                           self.tender_token),
                            {"data": {"status": "active"}})
        # check status
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertTrue(all([i['status'] == 'complete' for i in response.json['data']['lots']]))
        self.assertEqual(response.json['data']['status'], 'complete')


class TenderStage2UALotResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):

    initial_lots = [deepcopy(test_lots[0]) for i in range(3)]

    def test_create_tender_lot_invalid(self):
        """ Try create invalid lot """
        response = self.app.post_json('/tenders/some_id/lots',
                                      {'data': {'title': 'lot title', 'description': 'lot description'}}, status=404)
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
            {u'description':
                 u"Content-Type header should be one of ['application/json']", u'location': u'header',
             u'name': u'Content-Type'}
        ])

        response = self.app.post(request_path, 'data', content_type='application/json', status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u"location": u"body",
             u"name": u"data",
             u"description": u"Can't create lot for tender stage2"}
        ])

        response = self.app.post_json(request_path, 'data', status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u"location": u"body",
             u"name": u"data",
             u"description": u"Can't create lot for tender stage2"}
        ])

        response = self.app.post_json(request_path, {'not_data': {}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u"location": u"body",
             u"name": u"data",
             u"description": u"Can't create lot for tender stage2"}
        ])

        response = self.app.post_json(request_path, {'data': {}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u"location": u"body",
             u"name": u"data",
             u"description": u"Can't create lot for tender stage2"}
        ])

        response = self.app.post_json(request_path, {'data': {'invalid_field': 'invalid_value'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u"location": u"body",
             u"name": u"data",
             u"description": u"Can't create lot for tender stage2"}
        ])

        response = self.app.post_json(request_path, {'data': {'value': 'invalid_value'}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u"location": u"body",
             u"name": u"data",
             u"description": u"Can't create lot for tender stage2"}
        ])

        response = self.app.post_json(request_path, {'data': {
            'title': 'lot title',
            'description': 'lot description',
            'value': {'amount': '100.0'},
            'minimalStep': {'amount': '500.0'},
        }}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u"location": u"body",
             u"name": u"data",
             u"description": u"Can't create lot for tender stage2"}
        ])

    def test_create_tender_lot(self):
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], "Can't create lot for tender stage2")

        lot2 = deepcopy(test_lots[0])
        lot2['guarantee'] = {"amount": 100500, "currency": "USD"}
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': lot2},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], "Can't create lot for tender stage2")

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertNotIn('guarantee', response.json['data'])

        lot3 = deepcopy(test_lots[0])
        lot3['guarantee'] = {"amount": 500, "currency": "UAH"}
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': lot3}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], "Can't create lot for tender stage2")

        lot3['guarantee'] = {"amount": 500}
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': lot3}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], "Can't create lot for tender stage2")

        lot3['guarantee'] = {"amount": 20, "currency": "USD"}
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': lot3}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], "Can't create lot for tender stage2")

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertNotIn('guarantee', response.json['data'])

        self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                            {"data": {"guarantee": {'currency': 'EUR', 'amount': 300}}})
        response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token))

        self.assertNotIn('guarantee', response.json['data'])

        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], "Can't create lot for tender stage2")

        self.go_to_enquiryPeriod_end()
        response = self.app.post_json('/tenders/{}/lots'.format(self.tender_id), {'data': test_lots[0]}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')

        self.set_status('active.auction')

        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't create lot for tender stage2")

    def test_patch_tender_lot(self):

        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                                 self.lots[0]['id'],
                                                                                 self.tender_token),
                                       {"data": {"title": "new title"}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        response = self.app.get('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                          self.lots[0]['id'],
                                                                          self.tender_token))
        self.assertNotEqual(response.json['data']["title"], "new title")

        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                                 self.lots[0]['id'],
                                                                                 self.tender_token),
                                       {'data': {'guarantee': {'amount': 12}}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')

        response = self.app.get('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                          self.lots[0]['id'],
                                                                          self.tender_token))
        self.assertNotIn('guarantee', response.json['data'])

        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                                 self.lots[0]['id'],
                                                                                 self.tender_token),
                                       {"data": {"guarantee": {"currency": "USD"}}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        response = self.app.get('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                          self.lots[0]['id'],
                                                                          self.tender_token))
        self.assertNotIn('guarantee', response.json['data'])

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

        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, self.lots[0]['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertNotEqual(response.json['data']["title"], "new title")

        self.set_status('active.auction')

        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                                 self.lots[0]['id'],
                                                                                 self.tender_token),
                                       {"data": {"title": "other title"}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         u"Can't update lot for tender stage2")

    def test_patch_tender_currency(self):
        self.create_tender()
        lot = self.lots[0]
        self.assertEqual(lot['value']['currency'], "UAH")

        # update tender currency without mimimalStep currency change
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {'data': {'value': {'currency': 'GBP'}}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.json['errors'],
                         [{u'description': [u'currency should be identical to currency of value of tender'],
                           u'location': u'body',
                           u'name': u'minimalStep'}])

        # try update tender currency
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {'data': {'value': {'currency': 'GBP'},
                                                 'minimalStep': {'currency': 'GBP'}}})
        # log currency is updated too
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertEqual(lot['value']['currency'], "UAH")

        # try to update lot currency
        response = self.app.patch_json(
            '/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token),
            {"data": {"value": {"currency": "USD"}}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [{u"location": u"body",
                                                    u"name": u"data",
                                                    u"description": u"Can't update lot for tender stage2"}])
        # but the value stays unchanged
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertEqual(lot['value']['currency'], "UAH")  # it's still UAH

        # try to update minimalStep currency
        response = self.app.patch_json(
            '/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token),
            {"data": {"minimalStep": {"currency": "USD"}}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [{u"location": u"body",
                                                    u"name": u"data",
                                                    u"description": u"Can't update lot for tender stage2"}])
        # but the value stays unchanged
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertEqual(lot['minimalStep']['currency'], "UAH")

        # try to update lot minimalStep currency and lot value currency in single request
        response = self.app.patch_json(
            '/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token),
            {"data": {"value": {"currency": "USD"}, "minimalStep": {"currency": "USD"}}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [{u"location": u"body",
                                                    u"name": u"data",
                                                    u"description": u"Can't update lot for tender stage2"}])
        # but the value stays unchanged
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertEqual(lot['value']['currency'], "UAH")
        self.assertEqual(lot['minimalStep']['currency'], "UAH")

    def test_patch_tender_vat(self):
        # set tender VAT
        data = deepcopy(self.initial_data)
        data['value']['valueAddedTaxIncluded'] = True
        self.create_tender(initial_data=data)

        response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token))
        lot = response.json['data']['lots'][0]
        self.assertTrue(lot['value']['valueAddedTaxIncluded'])

        # Try update tender VAT
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {'data': {'value': {'valueAddedTaxIncluded': False},
                                                 'minimalStep': {'valueAddedTaxIncluded': False}}
                                        })
        self.assertEqual(response.status, '200 OK')
        # log VAT is not updated too
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertTrue(lot['value']['valueAddedTaxIncluded'])

        # try to update lot VAT
        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'],
                                                                                 self.tender_token),
                                       {'data': {'value': {'valueAddedTaxIncluded': True}}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [{u"location": u"body",
                                                    u"name": u"data",
                                                    u"description": u"Can't update lot for tender stage2"}])
        # but the value stays unchanged
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertTrue(lot['value']['valueAddedTaxIncluded'])

        # try to update minimalStep VAT
        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'],
                                                                                 self.tender_token),
                                       {"data": {"minimalStep": {"valueAddedTaxIncluded": True}}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [{u"location": u"body",
                                                    u"name": u"data",
                                                    u"description": u"Can't update lot for tender stage2"}])
        # but the value stays unchanged
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertTrue(lot['minimalStep']['valueAddedTaxIncluded'])

    def test_get_tender_lot(self):
        self.create_tender(initial_lots=self.initial_lots)
        response = self.app.get('/tenders/{}/lots'.format(self.tender_id))
        lot = response.json['data'][0]
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], 'active.tendering')

        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(set(response.json['data']), set(
            [u'id', u'title', u'date', u'description', u'minimalStep', u'value', u'status', u'auctionPeriod']))

        self.set_status('active.qualification')

        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot.pop('auctionPeriod')
        res = response.json['data']
        res.pop('auctionPeriod')
        self.assertEqual(res, lot)

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
        self.create_tender(initial_lots=self.initial_lots)
        response = self.app.get('/tenders/{}/lots'.format(self.tender_id))
        lot = response.json['data'][0]

        response = self.app.get('/tenders/{}/lots'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(set(response.json['data'][0]), set([u'id', u'date', u'title', u'description',
                                                             u'minimalStep', u'value', u'status', u'auctionPeriod']))

        self.set_status('active.qualification')

        response = self.app.get('/tenders/{}/lots'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot.pop('auctionPeriod')
        res = response.json['data'][0]
        res.pop('auctionPeriod')
        self.assertEqual(res, lot)

        response = self.app.get('/tenders/some_id/lots', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

    def test_delete_tender_lot(self):
        lot = self.lots[0]

        response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                             lot['id'],
                                                                             self.tender_token),
                                   status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]['description'], "Can't delete lot for tender stage2")

        response = self.app.delete('/tenders/{}/lots/some_id?acc_token={}'.format(self.tender_id,
                                                                                  self.tender_token),
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

        self.set_status('active.auction')

        response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                             lot['id'],
                                                                             self.tender_token), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't delete lot for tender stage2")

    def test_tender_lot_guarantee(self):
        lots = deepcopy(self.initial_lots)
        lots[0]['guarantee'] = {"amount": 20, "currency": "GBP"}
        self.create_tender(initial_lots=lots)
        lot = self.lots[0]
        lot_id = lot['id']
        response = self.app.get('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot_id, self.tender_token))
        self.assertEqual(response.json['data']['guarantee']['amount'], 20)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        lot = self.lots[1]
        lot_id = lot['id']
        response = self.app.get('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot_id, self.tender_token))
        self.assertNotIn('guarantee', response.json['data'])

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['guarantee']['amount'], 20)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

    def test_tender_lot_guarantee_v2(self):
        lots = deepcopy(self.initial_lots)
        lots[0]['guarantee'] = {"amount": 20, "currency": "GBP"}
        lots[1]['guarantee'] = {"amount": 40, "currency": "GBP"}
        self.create_tender(initial_lots=lots)
        lot = self.lots[0]
        lot_id = lot['id']
        response = self.app.get('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot_id, self.tender_token))
        self.assertEqual(response.json['data']['guarantee']['amount'], 20)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        lot = self.lots[1]
        lot_id = lot['id']
        response = self.app.get('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot_id, self.tender_token))
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 40)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['guarantee']['amount'], 60)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        lot2 = self.lots[1]
        lot2_id = lot2['id']
        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot2['id'],
                                                                                 self.tender_token),
                                       {'data': {'guarantee': {'amount': 50, 'currency': 'USD'}}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'], [{u"location": u"body",
                                                    u"name": u"data",
                                                    u"description": u"Can't update lot for tender stage2"}])

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 60)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                            {'data': {'guarantee': {'amount': 55}}})
        response = self.app.get('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token))
        self.assertEqual(response.json['data']['guarantee']['amount'], 60)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                            {'data': {'guarantee': {"amount": 35, "currency": "GBP"}}})

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 60)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        for l_id in (lot_id, lot2_id):
            response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                                     l_id,
                                                                                     self.tender_token),
                                           {'data': {'guarantee': {"amount": 0, "currency": "GBP"}}},
                                           status=403)
            self.assertEqual(response.status, '403 Forbidden')
            self.assertEqual(response.json['errors'], [{u"location": u"body",
                                                        u"name": u"data",
                                                        u"description": u"Can't update lot for tender stage2"}])
            response = self.app.get('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, l_id, self.tender_token))
            self.assertNotEqual(response.json['data']['guarantee']['amount'], 0)
            self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertIn('guarantee', response.json['data'])
        self.assertEqual(response.json['data']['guarantee']['amount'], 60)
        self.assertEqual(response.json['data']['guarantee']['currency'], "GBP")


class TenderStage2UALotEdgeCasesTest(BaseCompetitiveDialogUAStage2ContentWebTest, TenderStage2LotEdgeCasesMixin):
    initial_data = test_tender_stage2_data_ua
    initial_lots = [deepcopy(test_lots[0]) for i in range(2)]
    expected_status = "active.auction"

    def setUp(self):
        s2_bids = [deepcopy(bid) for bid in test_bids]
        for bid in s2_bids:
            # bid['tenderers'][0]['identifier']['id'] = '00000{}'.format(n)
            bid['tenderers'][0]['identifier']['id'] = self.initial_data['shortlistedFirms'][0]['identifier']['id']
            bid['tenderers'][0]['identifier']['scheme'] = self.initial_data['shortlistedFirms'][0]['identifier']['scheme']
        self.initial_bids = s2_bids
        super(TenderStage2UALotEdgeCasesTest, self).setUp()


class TenderStage2UALotFeatureResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_lots = [deepcopy(test_lots[0]) for i in range(2)]

    def test_tender_value(self):
        request_path = '/tenders/{}'.format(self.tender_id)
        response = self.app.get(request_path)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['value']['amount'],
                         sum([i['value']['amount'] for i in self.lots]))
        self.assertEqual(response.json['data']['minimalStep']['amount'],
                         min([i['minimalStep']['amount'] for i in self.lots]))

    def test_tender_features_invalid(self):
        request_path = '/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token)
        data = test_tender_data.copy()
        item = data['items'][0].copy()
        item['id'] = "1"
        data['items'] = [item]
        data['features'] = [
            {
                "featureOf": "lot",
                "relatedItem": self.lots[0]['id'],
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
        data['features'][0]["enum"][0]["value"] = 0.1
        data['features'].append(data['features'][0].copy())
        data['features'].append(data['features'][0].copy())
        data['features'].append(data['features'][0].copy())
        data['features'][1]["enum"][0]["value"] = 0.2
        data['features'][2]["enum"][0]["value"] = 0.3
        data['features'][3]["enum"][0]["value"] = 0.3
        response = self.app.patch_json(request_path, {'data': data}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'Sum of max value of all features for lot should be less then or equal to 99%'],
             u'location': u'body',
             u'name': u'features'}
        ])
        data['features'][1]["enum"][0]["value"] = 0.1
        data['features'].append(data['features'][0].copy())
        data['features'][2]["relatedItem"] = self.lots[1]['id']
        data['features'].append(data['features'][2].copy())
        response = self.app.patch_json(request_path, {'data': data})
        self.assertEqual(response.status, '200 OK')


class TenderStage2UALotBidderResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    # initial_status = 'active.tendering'
    initial_lots = deepcopy(test_lots)

    def test_create_tender_bidder_invalid(self):
        request_path = '/tenders/{}/bids'.format(self.tender_id)
        tenderers = self.create_tenderers()
        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': tenderers[0]}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'lotValues'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': tenderers[0],
                                                              'lotValues': [{'value': {'amount': 500}}]}},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'relatedLot': [u'This field is required.']}],
             u'location': u'body',
             u'name': u'lotValues'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': tenderers[0],
                                                              'lotValues': [{'value': {'amount': 500},
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

        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': tenderers[0],
                                                              'lotValues': [{"value": {"amount": 5000000},
                                                                             'relatedLot': self.lots[0]['id']}]
                                                              }},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'value': [u'value of bid should be less than value of lot']}],
             u'location': u'body',
             u'name': u'lotValues'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': tenderers[0],
                                                              'lotValues': [{"value": {"amount": 500,
                                                                                       'valueAddedTaxIncluded': False},
                                                                             'relatedLot': self.lots[0]['id']}]
                                                              }},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'value': [u'valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of lot']}], u'location': u'body', u'name': u'lotValues'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': tenderers[0],
                                                              'lotValues': [{"value": {"amount": 500,
                                                                                       'currency': "USD"},
                                                                             'relatedLot': self.lots[0]['id']}]
                                                              }},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'value': [u'currency of bid should be identical to currency of value of lot']}],
             u'location': u'body',
             u'name': u'lotValues'},
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': tenderers[0],
                                                              "value": {"amount": 500},
                                                              'lotValues': [{"value": {"amount": 500},
                                                                             'relatedLot': self.lots[0]['id']}]}
                                                     }, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'value should be posted for each lot of bid'], u'location': u'body', u'name': u'value'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': test_organization,
                                                              'lotValues': [{"value": {"amount": 500},
                                                                             'relatedLot': self.lots[0]['id']}]
                                                              }},
                                      status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u"invalid literal for int() with base 10: 'contactPoint'",
             u'location': u'body', u'name': u'data'},
        ])

    def test_patch_tender_bidder(self):
        lot_id = self.lots[0]['id']
        tenderers = self.create_tenderers()

        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                                'tenderers': tenderers[0],
                                                'lotValues': [{'value': {'amount': 500},
                                                               'relatedLot': lot_id}]}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bidder = response.json['data']
        lot = bidder['lotValues'][0]
        owner_token = response.json['access']['token']

        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id,
                                                                                 bidder['id'],
                                                                                 owner_token),
                                       {"data": {'tenderers': [{"name": u"Державне управління управлінням справами"}]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lotValues'][0]['date'], lot['date'])
        self.assertNotEqual(response.json['data']['tenderers'][0]['name'], bidder['tenderers'][0]['name'])

        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id,
                                                                                 bidder['id'],
                                                                                 owner_token),
                                       {"data": {'lotValues': [{"value": {"amount": 500},
                                                                'relatedLot': lot_id}],
                                                 'tenderers': [test_organization]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lotValues'][0]['date'], lot['date'])
        self.assertEqual(response.json['data']['tenderers'][0]['name'], bidder['tenderers'][0]['name'])

        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id,
                                                                                 bidder['id'],
                                                                                 owner_token),
                                       {"data": {'lotValues': [{"value": {"amount": 400}, 'relatedLot': lot_id}]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lotValues'][0]["value"]["amount"], 400)
        self.assertNotEqual(response.json['data']['lotValues'][0]['date'], lot['date'])

        self.set_status('complete')

        response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, bidder['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['lotValues'][0]["value"]["amount"], 400)

        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(
            self.tender_id, bidder['id'], owner_token), {"data": {'lotValues': [{"value": {"amount": 500},
                                                                                 'relatedLot': lot_id}]}},
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't update bid in current (complete) tender status")


class TenderStage2UALotFeatureBidderResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_lots = deepcopy(test_lots)
    initial_features = [
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
            "relatedItem": "3",
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

    def __init__(self, *args, **kwargs):
        self.id_first_lot = uuid4().hex
        self.id_first_item = uuid4().hex
        self.initial_lots[0]['id'] = self.id_first_lot
        self.initial_data = deepcopy(self.initial_data)
        self.initial_data['items'][0]['id'] = self.id_first_item
        self.initial_features[0]['relatedItem'] = self.id_first_lot
        self.initial_features[1]['relatedItem'] = self.id_first_item
        super(TenderStage2UALotFeatureBidderResourceTest, self).__init__(*args, **kwargs)

    def setUp(self):
        super(TenderStage2UALotFeatureBidderResourceTest, self).setUp()
        self.app.authorization = ('Basic', ('broker', ''))
        self.lot_id = self.initial_lots[0]['id']
        self.create_tender(initial_lots=self.initial_lots, features=self.initial_features)

    def test_create_tender_bidder_invalid(self):
        request_path = '/tenders/{}/bids'.format(self.tender_id)
        tenderers = self.create_tenderers()
        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': tenderers[0]}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        for error in response.json['errors']:
             self.assertIn(
                 error, [{u'description': [u'This field is required.'], u'location': u'body', u'name': u'lotValues'},
                         {u'description': [u'All features parameters is required.'], u'location': u'body', u'name': u'parameters'}]
             )

        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': tenderers[0], 'lotValues': [{"value": {"amount": 500}}]}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'relatedLot': [u'This field is required.']}], u'location': u'body', u'name': u'lotValues'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': tenderers[0], 'lotValues': [{"value": {"amount": 500}, 'relatedLot': "0" * 32}]}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'relatedLot': [u'relatedLot should be one of lots']}], u'location': u'body', u'name': u'lotValues'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': tenderers[0], 'lotValues': [{"value": {"amount": 5000000}, 'relatedLot': self.lot_id}]}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'value': [u'value of bid should be less than value of lot']}], u'location': u'body', u'name': u'lotValues'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': tenderers[0], 'lotValues': [{"value": {"amount": 500, 'valueAddedTaxIncluded': False}, 'relatedLot': self.lot_id}]}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'value': [u'valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of lot']}], u'location': u'body', u'name': u'lotValues'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': tenderers[0], 'lotValues': [{"value": {"amount": 500, 'currency': "USD"}, 'relatedLot': self.lot_id}]}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'value': [u'currency of bid should be identical to currency of value of lot']}], u'location': u'body', u'name': u'lotValues'},
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': test_organization, 'lotValues': [{"value": {"amount": 500}, 'relatedLot': self.lot_id}]}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u"invalid literal for int() with base 10: 'contactPoint'", u'location': u'body', u'name': u'data'},
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': tenderers[0], 'lotValues': [{"value": {"amount": 500}, 'relatedLot': self.lot_id}]}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'All features parameters is required.'], u'location': u'body', u'name': u'parameters'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': tenderers[0], 'lotValues': [{"value": {"amount": 500}, 'relatedLot': self.lot_id}], 'parameters': [{"code": "code_item", "value": 0.01}]}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'All features parameters is required.'], u'location': u'body', u'name': u'parameters'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': tenderers[0], 'lotValues': [{"value": {"amount": 500}, 'relatedLot': self.lot_id}], 'parameters': [{"code": "code_invalid", "value": 0.01}]}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'code': [u'code should be one of feature code.']}], u'location': u'body', u'name': u'parameters'}
        ])

        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': tenderers[0], 'lotValues': [{"value": {"amount": 500}, 'relatedLot': self.lot_id}], 'parameters': [
            {"code": "code_item", "value": 0.01},
            {"code": "code_tenderer", "value": 0},
            {"code": "code_lot", "value": 0.01},
        ]}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'value': [u'value should be one of feature value.']}], u'location': u'body', u'name': u'parameters'}
        ])

    def test_create_tender_bidder(self):
        request_path = '/tenders/{}/bids'.format(self.tender_id)
        tenderers = self.create_tenderers()
        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': tenderers[0],
                                                              'lotValues': [{"value": {"amount": 500},
                                                                             'relatedLot': self.lot_id}],
                                                              'parameters': [{"code": "code_item", "value": 0.01},
                                                                             {"code": "code_tenderer", "value": 0.01},
                                                                             {"code": "code_lot", "value": 0.01}]}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bidder = response.json['data']
        self.assertEqual(bidder['tenderers'][0]['name'], test_organization['name'])
        self.assertIn('id', bidder)
        self.assertIn(bidder['id'], response.headers['Location'])

        self.set_status('complete')

        response = self.app.post_json(request_path, {'data': {'selfEligible': True, 'selfQualified': True,
                                                              'tenderers': tenderers[0],
                                                              'lotValues': [{"value": {"amount": 500},
                                                                             'relatedLot': self.lot_id}],
                                                              'parameters': [{"code": "code_item", "value": 0.01},
                                                                             {"code": "code_tenderer", "value": 0.01},
                                                                             {"code": "code_lot", "value": 0.01}]}},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add bid in current (complete) tender status")


class TenderStage2UALotProcessTest(BaseCompetitiveDialogUAStage2ContentWebTest):

    initial_data = test_tender_stage2_data_ua

    def setUp(self):
        super(BaseCompetitiveDialogUAStage2ContentWebTest, self).setUp()
        self.app.authorization = ('Basic', ('broker', ''))

    def create_tenderers(self, count=1):
        tenderers = []
        for i in xrange(count):
            tenderer = deepcopy(test_bids[0]["tenderers"])
            tenderer[0]['identifier']['id'] = self.initial_data['shortlistedFirms'][i if i < 3 else 3]['identifier']['id']
            tenderer[0]['identifier']['scheme'] = self.initial_data['shortlistedFirms'][i if i < 3 else 3]['identifier']['scheme']
            tenderers.append(tenderer)
        return tenderers

    def create_tender(self, initial_lots, features=None):
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))
        data = deepcopy(self.initial_data)
        if initial_lots:
            lots = []
            for i in initial_lots:
                lot = deepcopy(i)
                if 'id' not in lot:
                    lot['id'] = uuid4().hex
                lots.append(lot)
            data['lots'] = self.initial_lots = lots
            for i, item in enumerate(data['items']):
                item['relatedLot'] = lots[i % len(lots)]['id']
            for firm in data['shortlistedFirms']:
                firm['lots'] = [dict(id=lot['id']) for lot in lots]
            self.lots_id = [lot['id'] for lot in lots]
        if features:
            for feature in features:
                if feature['featureOf'] == 'lot':
                    feature['relatedItem'] = data['lots'][0]['id']
                if feature['featureOf'] == 'item':
                    feature['relatedItem'] = data['items'][0]['id']
            data['features'] = self.features = features
        response = self.app.post_json('/tenders', {'data': data})
        tender = response.json['data']
        self.tender = tender
        self.tender_token = response.json['access']['token']
        self.tender_id = tender['id']
        self.app.authorization = ('Basic', ('competitive_dialogue', ''))
        self.app.patch_json('/tenders/{id}?acc_token={token}'.format(id=self.tender_id,
                                                                     token=self.tender_token),
                            {'data': {'status': 'draft.stage2'}})

        self.app.authorization = ('Basic', ('broker', ''))
        self.app.patch_json('/tenders/{id}?acc_token={token}'.format(id=self.tender_id,
                                                                     token=self.tender_token),
                            {'data': {'status': 'active.tendering'}})
        self.app.authorization = auth

    def test_1lot_0bid(self):
        self.create_tender(initial_lots=test_lots)
        # switch to active.tendering
        response = self.set_status('active.tendering', {"lots": [{"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}]})
        self.assertIn("auctionPeriod", response.json['data']['lots'][0])
        # switch to unsuccessful
        response = self.set_status('active.auction', {"lots": [{"auctionPeriod": {"startDate": None}}],
                                                      'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']["lots"][0]['status'], 'unsuccessful')
        self.assertEqual(response.json['data']['status'], 'unsuccessful')

    def test_1lot_1bid(self):
        self.create_tender(initial_lots=test_lots)
        tenderers = self.create_tenderers()
        # switch to active.tendering
        response = self.set_status('active.tendering', {"lots": [{"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}]})
        self.assertIn("auctionPeriod", response.json['data']['lots'][0])
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                                'tenderers': tenderers[0],
                                                'lotValues': [{"subcontractingDetails": "test",
                                                               "value": {"amount": 500},
                                                               'relatedLot': self.lots_id[0]}]}})
        # switch to active.qualification
        response = self.set_status('active.auction', {"lots": [{"auctionPeriod": {"startDate": None}}],
                                                      'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']["lots"][0]['status'], 'unsuccessful')
        self.assertEqual(response.json['data']['status'], 'unsuccessful')

    def test_1lot_1bid_patch(self):
        self.create_tender(initial_lots=test_lots)
        tenderers = self.create_tenderers()
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                                'tenderers': tenderers[0],
                                                'lotValues': [{"value": {"amount": 500},
                                                               'relatedLot': self.lots_id[0]}]}})
        bid_id = response.json['data']['id']
        bid_token = response.json['access']['token']

        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                                 self.lots_id[0],
                                                                                 self.tender_token),
                                       {'data': {'value': {'amount': 499}}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'][0]['description'], u"Can't update lot for tender stage2")

        response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id,
                                                                          bid_id,
                                                                          bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active')

    def test_1lot_2bid(self):
        self.create_tender(initial_lots=test_lots)
        tenderers = self.create_tenderers(2)
        # switch to active.tendering
        response = self.set_status('active.tendering', {"lots": [{"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}]})
        self.assertIn("auctionPeriod", response.json['data']['lots'][0])
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                                'tenderers': tenderers[0],
                                                'lotValues': [{"subcontractingDetails": "test",
                                                               "value": {"amount": 450}, 'relatedLot': self.lots_id[0]}]
                                                }
                                       })
        bid_id = response.json['data']['id']
        bid_token = response.json['access']['token']
        # create second bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                                'tenderers': tenderers[1],
                                                'lotValues': [{"value": {"amount": 475},
                                                               'relatedLot': self.lots_id[0]}]}})
        # switch to active.auction
        self.set_status('active.auction')
        # get auction info
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        # posting auction urls
        response = self.app.patch_json('/tenders/{}/auction/{}'.format(self.tender_id, self.lots_id[0]), {
            'data': {
                'lots': [
                    {
                        'id': i['id'],
                        'auctionUrl': 'https://tender.auction.url'
                    }
                    for i in response.json['data']['lots']
                ],
                'bids': [
                    {
                        'id': i['id'],
                        'lotValues': [
                            {
                                'relatedLot': j['relatedLot'],
                                'participationUrl': 'https://tender.auction.url/for_bid/{}'.format(i['id'])
                            }
                            for j in i['lotValues']
                        ],
                    }
                    for i in auction_bids_data
                ]
            }
        })
        # view bid participationUrl
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid_id, bid_token))
        self.assertEqual(response.json['data']['lotValues'][0]['participationUrl'],
                         'https://tender.auction.url/for_bid/{}'.format(bid_id))
        # posting auction results
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, self.lots_id[0]),
                                      {'data': {'bids': auction_bids_data}})
        # get awards
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.tender_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
        # set award as active
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                            {"data": {"status": "active", "qualified": True, "eligible": True}})
        # get contract id
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        contract_id = response.json['data']['contracts'][-1]['id']
        # after stand still period
        self.set_status('complete', {'status': 'active.awarded'})
        # time travel
        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)
        # sign contract
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id,
                                                                           contract_id,
                                                                           self.tender_token),
                            {"data": {"status": "active"}})
        # check status
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']["lots"][0]['status'], 'complete')
        self.assertEqual(response.json['data']['status'], 'complete')

    def test_1lot_3bid_1un(self):
        self.create_tender(initial_lots=test_lots)
        tenderers = self.create_tenderers(3)
        response = self.set_status('active.tendering', {"lots": [{"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}]})
        self.assertIn("auctionPeriod", response.json['data']['lots'][0])
        # create bids
        bids_data = {}
        for i in range(3):

            self.app.authorization = ('Basic', ('broker', ''))
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                          {'data': {'selfEligible': True, 'selfQualified': True,
                                                    'tenderers': tenderers[i],
                                                    'lotValues': [{'value': {'amount': 450},
                                                                   'relatedLot': self.lots_id[0]}]}})
            bids_data[response.json['data']['id']] = response.json['access']['token']

        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                                 self.lots_id[0],
                                                                                 self.tender_token),
                                       {'data': {'value': {'amount': 1000}}},
                                       status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.json['errors'][0]['description'], u"Can't update lot for tender stage2")
        # create second bid
        for bid_id, bid_token in bids_data.items()[:-1]:

            self.app.authorization = ('Basic', ('broker', ''))
            response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid_id, bid_token),
                                          {'data': {'status': "active"}})
            # bids_data[response.json['data']['id']] = response.json['access']['token']
        # switch to active.auction
        self.set_status('active.auction')
        # get auction info
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        # posting auction urls

        auction_data = {
            'data': {
                'lots': [
                    {
                        'id': i['id'],
                        'auctionUrl': 'https://tender.auction.url'
                    }
                    for i in response.json['data']['lots']
                ],
                'bids': []
            }
        }
        for i in auction_bids_data:
            if i.get("status", "active") == "active":
                auction_data["data"]["bids"].append({
                        'id': i['id'],
                        'lotValues': [
                            {
                                'relatedLot': j['relatedLot'],
                                'participationUrl': 'https://tender.auction.url/for_bid/{}'.format(i['id'])
                            }
                            for j in i['lotValues']
                        ],
                    })
            else:
                auction_data["data"]["bids"].append({'id': i['id']})

        response = self.app.patch_json('/tenders/{}/auction/{}'.format(self.tender_id, self.lots_id[0]), auction_data)
        # posting auction results
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, self.lots_id[0]),
                                      {'data': {'bids': auction_bids_data}})
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.tender_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]
        # set award as active
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                            {"data": {"status": "active", "qualified": True, "eligible": True}})
        # get contract id
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        contract_id = response.json['data']['contracts'][-1]['id']
        # after stand still period
        self.set_status('complete', {'status': 'active.awarded'})
        # time travel
        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)
        # sign contract
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id,
                                                                           contract_id,
                                                                           self.tender_token),
                            {"data": {"status": "active"}})
        # check status
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']["lots"][0]['status'], 'complete')
        self.assertEqual(response.json['data']['status'], 'complete')

    def test_2lot_0bid(self):
        self.create_tender(initial_lots=test_lots*2)
        # switch to active.tendering
        response = self.set_status('active.tendering', {"lots": [
            {"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}
            for i in self.lots_id
        ]})
        self.assertTrue(all(["auctionPeriod" in i for i in response.json['data']['lots']]))
        # switch to unsuccessful
        response = self.set_status('active.auction', {
            "lots": [
                {"auctionPeriod": {"startDate": None}}
                for i in self.lots_id
            ],
            'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertTrue(all([i['status'] == 'unsuccessful' for i in response.json['data']['lots']]))
        self.assertEqual(response.json['data']['status'], 'unsuccessful')

    def test_2lot_2can(self):
        self.create_tender(initial_lots=test_lots*2)
        # switch to active.tendering
        response = self.set_status('active.tendering', {"lots": [
            {"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}
            for i in self.lots_id
        ]})
        self.assertTrue(all(["auctionPeriod" in i for i in response.json['data']['lots']]))
        # cancel every lot
        for lot_id in self.lots_id:
            response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(self.tender_id,
                                                                                          self.tender_token),
                                          {'data': {'reason': 'cancellation reason',
                                                    'status': 'active',
                                                    "cancellationOf": "lot",
                                                    "relatedLot": lot_id}})
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertTrue(all([i['status'] == 'cancelled' for i in response.json['data']['lots']]))
        self.assertEqual(response.json['data']['status'], 'cancelled')

    def test_2lot_1bid_0com_1can(self):
        self.create_tender(initial_lots=test_lots*2)
        tenderers = self.create_tenderers()
        # switch to active.tendering
        response = self.set_status('active.tendering', {"lots": [
            {"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}
            for i in self.lots_id
        ]})
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                                'tenderers': tenderers[0],
                                                'lotValues': [{"value": {"amount": 500}, 'relatedLot': lot_id}
                                                              for lot_id in self.lots_id]}
                                       })
        # switch to active.qualification
        response = self.set_status('active.auction', {
            "lots": [
                {"auctionPeriod": {"startDate": None}}
                for i in self.lots_id
            ],
            'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'unsuccessful')

    def test_2lot_2bid_1lot_del(self):
        self.create_tender(initial_lots=test_lots*2)
        tenderers = self.create_tenderers(2)
        self.app.authorization = ('Basic', ('broker', ''))
        # switch to active.tendering
        response = self.set_status('active.tendering',
                                   {"lots": [{"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}
                                             for i in self.lots_id]})
        # create bid
        bids = []
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True,
                                                'selfQualified': True,
                                                'tenderers': tenderers[0],
                                                'lotValues': [{"value": {"amount": 500}, 'relatedLot': lot_id}
                                                              for lot_id in self.lots_id]}
                                       })
        bids.append(response.json)
        # create second bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True,
                                                'selfQualified': True,
                                                'tenderers': tenderers[1],
                                                'lotValues': [{"value": {"amount": 500}, 'relatedLot': lot_id}
                                                              for lot_id in self.lots_id]}
                                       })
        bids.append(response.json)
        response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id,
                                                                             self.lots_id[0],
                                                                             self.tender_token),
                                   status=403)

    def test_2lot_1bid_2com_1win(self):
        self.create_tender(initial_lots=test_lots)
        tenderers = self.create_tenderers()
        # switch to active.tendering
        self.set_status('active.tendering',
                        {"lots": [{"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}
                                  for i in self.lots_id]})
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                           {'data': {'selfEligible': True,
                                     'selfQualified': True,
                                     'tenderers': tenderers[0],
                                     'lotValues': [{"value": {"amount": 500}, 'relatedLot': lot_id}
                                                   for lot_id in self.lots_id]}
                            })
        # switch to active.qualification
        self.set_status('active.auction',
                        {"lots": [{"auctionPeriod": {"startDate": None}} for i in self.lots_id],
                         'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        for lot_id in self.lots_id:
            # get awards
            self.app.authorization = ('Basic', ('broker', ''))
            response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.tender_token))
            # get pending award
            if len([i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == lot_id]) == 0:
                return
            award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == lot_id][0]

            # set award as active
            self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id,
                                                                            award_id,
                                                                            self.tender_token),
                                {"data": {"status": "active"}})
            # get contract id
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            contract_id = response.json['data']['contracts'][-1]['id']
            # after stand still period
            self.set_status('complete', {'status': 'active.awarded'})
            # time travel
            tender = self.db.get(self.tender_id)
            for i in tender.get('awards', []):
                i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
            self.db.save(tender)
            # sign contract
            self.app.authorization = ('Basic', ('broker', ''))
            self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id,
                                                                               contract_id,
                                                                               self.tender_token),
                                {"data": {"status": "active"}})
        # check status
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertTrue(all([i['status'] == 'complete' for i in response.json['data']['lots']]))
        self.assertEqual(response.json['data']['status'], 'complete')

    def test_2lot_1bid_0com_0win(self):
        self.create_tender(initial_lots=test_lots*2)
        tenderers = self.create_tenderers()
        # switch to active.tendering
        response = self.set_status('active.tendering',
                                   {"lots": [{"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}
                                             for i in self.lots_id]})
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                           {'data': {'selfEligible': True, 'selfQualified': True,
                                     'tenderers': tenderers[0], 'lotValues': [{"value": {"amount": 500},
                                                                                      'relatedLot': lot_id}
                                                                                     for lot_id in self.lots_id]}
                            })
        # switch to active.qualification
        self.set_status('active.auction', {"lots": [{"auctionPeriod": {"startDate": None}}
                                                    for i in self.lots_id],
                                           'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertTrue(all([i['status'] == 'unsuccessful' for i in response.json['data']['lots']]))
        self.assertEqual(response.json['data']['status'], 'unsuccessful')

    def test_2lot_1bid_1com_1win(self):
        self.create_tender(initial_lots=test_lots*2)
        tenderers = self.create_tenderers()
        # switch to active.tendering
        self.set_status('active.tendering',
                        {"lots": [{"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}
                                  for i in self.lots_id]})
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                           {'data': {'selfEligible': True,
                                     'selfQualified': True,
                                     'tenderers': tenderers[0],
                                     'lotValues': [{"value": {"amount": 500}, 'relatedLot': lot_id}
                                                   for lot_id in self.lots_id]}
                            })
        # switch to active.qualification
        self.set_status('active.auction', {"lots": [{"auctionPeriod": {"startDate": None}}
                                                    for i in self.lots_id],
                                           'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'unsuccessful')

    def test_2lot_2bid_2com_2win(self):
        self.create_tender(initial_lots=test_lots*2)
        tenderers = self.create_tenderers(2)
        # switch to active.tendering
        self.set_status('active.tendering',
                        {"lots": [{"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}
                                  for i in self.lots_id]})
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                           {'data': {'selfEligible': True,
                                     'selfQualified': True,
                                     'tenderers': tenderers[0],
                                     'lotValues': [{"value": {"amount": 500}, 'relatedLot': lot_id}
                                                   for lot_id in self.lots_id]}
                            })
        # create second bid
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                           {'data': {'selfEligible': True,
                                     'selfQualified': True,
                                     'tenderers': tenderers[1],
                                     'lotValues': [{"value": {"amount": 500}, 'relatedLot': lot_id}
                                                   for lot_id in self.lots_id]}
                            })
        # switch to active.auction
        self.set_status('active.auction')
        # get auction info
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        for lot_id in self.lots_id:
            # posting auction urls
            response = self.app.patch_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id), {
                'data': {
                    'lots': [
                        {
                            'id': i['id'],
                            'auctionUrl': 'https://tender.auction.url'
                        }
                        for i in response.json['data']['lots']
                    ],
                    'bids': [
                        {
                            'id': i['id'],
                            'lotValues': [
                                {
                                    'relatedLot': j['relatedLot'],
                                    'participationUrl': 'https://tender.auction.url/for_bid/{}'.format(i['id'])
                                }
                                for j in i['lotValues']
                            ],
                        }
                        for i in auction_bids_data
                    ]
                }
            })
            # posting auction results
            self.app.authorization = ('Basic', ('auction', ''))
            response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id),
                                          {'data': {'bids': auction_bids_data}})
        # for first lot
        lot_id = self.lots_id[0]
        # get awards
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.tender_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == lot_id][0]
        # set award as active
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                            {"data": {"status": "active", "qualified": True, "eligible": True}})
        # get contract id
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        contract_id = response.json['data']['contracts'][-1]['id']
        # after stand still period
        self.set_status('complete', {'status': 'active.awarded'})
        # time travel
        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)
        # sign contract
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id, contract_id, self.tender_token),
                            {"data": {"status": "active"}})
        # for second lot
        lot_id = self.lots_id[1]
        # get awards
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.tender_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == lot_id][0]
        # set award as unsuccessful
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                            {"data": {"status": "unsuccessful"}})
        # get awards
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, self.tender_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == lot_id][0]
        # set award as active
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, self.tender_token),
                            {"data": {"status": "active", "qualified": True, "eligible": True}})
        # get contract id
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        contract_id = response.json['data']['contracts'][-1]['id']
        # after stand still period
        self.set_status('complete', {'status': 'active.awarded'})
        # time travel
        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)
        # sign contract
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(self.tender_id,
                                                                           contract_id,
                                                                           self.tender_token),
                            {"data": {"status": "active"}})
        # check status
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertTrue(all([i['status'] == 'complete' for i in response.json['data']['lots']]))
        self.assertEqual(response.json['data']['status'], 'complete')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderStage2EULotResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EULotBidderResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EULotFeatureBidderResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EULotProcessTest))
    suite.addTest(unittest.makeSuite(TenderStage2UALotResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UALotFeatureResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UALotBidderResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UALotFeatureBidderResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
