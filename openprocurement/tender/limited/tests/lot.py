# -*- coding: utf-8 -*-
from openprocurement.tender.limited.tests.base import (
    BaseTenderContentWebTest, test_tender_negotiation_data, test_lots,
    test_tender_negotiation_quick_data)


class TenderLotNegotiationResourceTest(BaseTenderContentWebTest):
    initial_status = 'active'
    initial_data = test_tender_negotiation_data
    initial_bids = None  # test_bids

    def test_create_tender_lot_invalid(self):
        response = self.app.post_json('/tenders/some_id/lots',
                                      {'data': {'title': 'lot title', 'description': 'lot description'}},
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
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'value'},
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

        response = self.app.post_json(request_path, {'data': {'value': 'invalid_value'}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [
                u'Please use a mapping for this field or Value instance instead of unicode.'],
                u'location': u'body',
                u'name': u'value'}
        ])

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

        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': lot}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'Lot id should be uniq for all lots'], u'location': u'body', u'name': u'lots'}
        ])

    def test_create_complete_tender_lot(self):
        """ Can't create lot when tender status is complete """
        self.set_status('complete')

        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u"location": u"body",
             u"name": u"data",
             u"description": u"Can't add lot in current (complete) tender status"}
        ])

    def test_create_cancelled_tender_lot(self):
        """ Can't create lot when tender status is cancelled """
        self.set_status('cancelled')

        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u"location": u"body",
             u"name": u"data",
             u"description": u"Can't add lot in current (cancelled) tender status"}
        ])

    def test_create_unsuccessful_tender_lot(self):
        """ Can't create lot when tender status is unsuccessful """
        self.set_status('unsuccessful')

        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]},
                                      status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u"location": u"body",
             u"name": u"data",
             u"description": u"Can't add lot in current (unsuccessful) tender status"}
        ])

    def test_patch_tender_lot(self):
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']

        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(
            self.tender_id, lot['id'], self.tender_token),
            {"data": {"title": "new title"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["title"], "new title")

        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(
            self.tender_id, lot['id'], self.tender_token),
            {"data": {"description": "new description"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["description"], "new description")

        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(
            self.tender_id, lot['id'], self.tender_token),
            {"data": {"value": {"amount": 400}}})

        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["value"]["amount"], 400)

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

        response = self.app.patch_json('/tenders/some_id/lots/some_id', {"data": {"title": "other title"}}, status=404)
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

        self.set_status('complete')

        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(
            self.tender_id, lot['id'], self.tender_token),
            {"data": {"title": "other title"}},
            status=403)

        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't update lot in current (complete) tender status")

    def test_patch_tender_currency(self):
        # create lot
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertEqual(lot['value']['currency'], "UAH")

        # update tender currency
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {"value": {"currency": "GBP"}}})

        self.assertEqual(response.status, '200 OK')
        # log currency is updated too
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertEqual(lot['value']['currency'], "GBP")

        # try to update lot currency
        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token),
                                       {"data": {"value": {"currency": "USD"}}})
        self.assertEqual(response.status, '200 OK')
        # but the value stays unchanged
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertEqual(lot['value']['currency'], "GBP")

        # try to update lot minimalStep currency and lot value currency in single request
        response = self.app.patch_json('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token),
                                       {"data": {"value": {"currency": "USD"}}})
        self.assertEqual(response.status, '200 OK')
        # but the value stays unchanged
        response = self.app.get('/tenders/{}/lots/{}'.format(self.tender_id, lot['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']
        self.assertEqual(lot['value']['currency'], "GBP")

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
                                       {"data": {"value": {"valueAddedTaxIncluded": False}}})

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

        # try to update value VAT in single request
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

    def test_delete_unsuccessful_tender_lot(self):
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']

        response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(
            self.tender_id, lot['id'], self.tender_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], lot)

        response = self.app.delete('/tenders/{}/lots/some_id?acc_token={}'.format(
            self.tender_id, self.tender_token),
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
                                       {"data": {
                                           "items": [{'relatedLot': lot['id']}]}
                                       })
        self.assertEqual(response.status, '200 OK')

        response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(
            self.tender_id, lot['id'], self.tender_token),
            status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'relatedLot': [u'relatedLot should be one of lots']}],
             u'location': u'body',
             u'name': u'items'}
        ])
        self.set_status('unsuccessful')

        response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(
            self.tender_id, lot['id'], self.tender_token),
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't delete lot in current (unsuccessful) tender status")

        response = self.app.get('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token))
        self.assertEqual(response.status, '200 OK')

    def test_delete_tender_lot(self):
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']

        response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(
            self.tender_id, lot['id'], self.tender_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], lot)

        response = self.app.delete('/tenders/{}/lots/some_id?acc_token={}'.format(
            self.tender_id, self.tender_token),
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
                                       {"data": {
                                           "items": [{'relatedLot': lot['id']}]}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(
            self.tender_id, lot['id'], self.tender_token),
            status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'relatedLot': [u'relatedLot should be one of lots']}],
             u'location': u'body',
             u'name': u'items'}
        ])

        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                       {"data": {
                                           "items": [{'relatedLot': None}]}})
        self.assertEqual(response.status, '200 OK')

        response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(
            self.tender_id, lot['id'], self.tender_token))

        self.assertEqual(response.status, '200 OK')

        response = self.app.get('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token),
                                status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'lot_id'}
        ])

    def test_delete_complete_tender_lot(self):
        response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(self.tender_id, self.tender_token),
                                      {'data': test_lots[0]})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        lot = response.json['data']

        response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(
            self.tender_id, lot['id'], self.tender_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], lot)

        response = self.app.delete('/tenders/{}/lots/some_id?acc_token={}'.format(
            self.tender_id, self.tender_token),
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
                                       {"data": {
                                           "items": [{'relatedLot': lot['id']}]}
                                       })
        self.assertEqual(response.status, '200 OK')

        response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(
            self.tender_id, lot['id'], self.tender_token),
            status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [{u'relatedLot': [u'relatedLot should be one of lots']}],
             u'location': u'body',
             u'name': u'items'}
        ])
        self.set_status('complete')

        response = self.app.delete('/tenders/{}/lots/{}?acc_token={}'.format(
            self.tender_id, lot['id'], self.tender_token),
            status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"],
                         "Can't delete lot in current (complete) tender status")

        response = self.app.get('/tenders/{}/lots/{}?acc_token={}'.format(self.tender_id, lot['id'], self.tender_token))
        self.assertEqual(response.status, '200 OK')


class TenderLotNegotiationQuickResourceTest(TenderLotNegotiationResourceTest):

    initial_data = test_tender_negotiation_quick_data