# -*- coding: utf-8 -*-
from openprocurement.tender.belowthreshold.tests.auction_blanks import update_patch_data
from openprocurement.frameworkagreement.cfaua.constants import MaxAwards


def post_tender_auction_all_awards_pending(self):
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': {}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't report auction results in current ({}) tender status".format(
                         self.forbidden_auction_actions_status))

    self.set_status('active.auction')

    patch_data = {'bids': []}
    for x in range(self.min_bids_number):
        patch_data['bids'].append({
            "id": self.initial_bids[x]['id'],
            "value": {
                "amount": 409 + x * 10,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            }
        })

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    tender = response.json['data']

    for x in range(self.min_bids_number):
        self.assertEqual(tender["bids"][x]['value']['amount'], patch_data["bids"][x]['value']['amount'])
        self.assertEqual(tender["awards"][x]['status'], 'pending')  # all awards are in pending status

    response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')

    self.app.authorization = ('Basic', ('broker', ''))
    awards = response.json['data']

    self.app.patch_json(
        '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, awards[0]['id'], self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}})

    # try to switch not all awards qualified
    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                   {"data": {"status": 'active.qualification.stand-still'}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.json['errors'][0]["description"],
                     u"Can't switch to 'active.qualification.stand-still' while not all awards are qualified")

    for award in awards[1:]:
        response = self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award['id'], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

    response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token),
                                   {"data": {"status": 'active.qualification.stand-still'}})
    self.assertEqual(response.json['data']['status'], 'active.qualification.stand-still')

    # switch to active.awarded
    self.set_status('active.awarded', {"id": self.tender_id, 'status': 'active.qualification.stand-still'})
    self.app.authorization = ('Basic', ('chronograph', ''))
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.json['data']['status'], "active.awarded")

    self.assertIn('agreements', response.json['data'])


def post_tender_auction(self):
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': {}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't report auction results in current ({}) tender status".format(
                         self.forbidden_auction_actions_status))

    self.set_status('active.auction')

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id),
                                  {'data': {'bids': [{'invalid_field': 'invalid_value'}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'invalid_field': u'Rogue field'}, u'location': u'body', u'name': u'bids'}
    ])

    patch_data = {
        'bids': [
            {
                "id": self.initial_bids[-1]['id'],
                "value": {
                    "amount": 409,
                    "currency": "UAH",
                    "valueAddedTaxIncluded": True
                }
            }
        ]
    }

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Number of auction results did not match the number of tender bids")

    update_patch_data(self, patch_data, key='value', start=-2, interval=-1)

    patch_data['bids'][-1]['id'] = "some_id"

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], {u'id': [u'Hash value is wrong length.']})

    patch_data['bids'][-1]['id'] = "00000000000000000000000000000000"

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Auction bids should be identical to the tender bids")

    patch_data['bids'][-1]['id'] = self.initial_bids[0]['id']

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    tender = response.json['data']
    self.assertNotEqual(tender["bids"][0]['value']['amount'], self.initial_bids[0]['value']['amount'])
    self.assertNotEqual(tender["bids"][-1]['value']['amount'], self.initial_bids[-1]['value']['amount'])
    self.assertEqual(tender["bids"][0]['value']['amount'], patch_data["bids"][-1]['value']['amount'])
    self.assertEqual(tender["bids"][-1]['value']['amount'], patch_data["bids"][0]['value']['amount'])
    self.assertEqual('active.qualification', tender["status"])
    self.assertIn("tenderers", tender["bids"][0])
    self.assertIn("name", tender["bids"][0]["tenderers"][0])

    if len(self.initial_bids) > MaxAwards:
        self.assertEqual(len(tender['awards']), MaxAwards)
    else:
        self.assertLessEqual(len(tender['awards']), MaxAwards)

    for x in list(range(self.min_bids_number))[:MaxAwards]:
        self.assertEqual(tender["awards"][x]['bid_id'], patch_data["bids"][x]['id'])
        self.assertEqual(tender["awards"][x]['value']['amount'], patch_data["bids"][x]['value']['amount'])
        self.assertEqual(tender["awards"][x]['suppliers'], self.initial_bids[x]['tenderers'])

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't report auction results in current (active.qualification) tender status")


# TenderLotAuctionResourceTestMixin


def post_tender_lot_auction(self):
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': {}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't report auction results in current ({}) tender status".format(
                         self.forbidden_auction_actions_status))

    self.set_status('active.auction')

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id),
                                  {'data': {'bids': [{'invalid_field': 'invalid_value'}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'invalid_field': u'Rogue field'}, u'location': u'body', u'name': u'bids'}
    ])

    patch_data = {
        'bids': [
            {
                "id": self.initial_bids[-1]['id'],
                'lotValues': [
                    {
                        "value": {
                            "amount": 409,
                            "currency": "UAH",
                            "valueAddedTaxIncluded": True
                        }
                    }
                ]
            }
        ]
    }

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Number of auction results did not match the number of tender bids")

    update_patch_data(self, patch_data, key='lotValues', start=-2, interval=-1)

    patch_data['bids'][-1]['id'] = "some_id"

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], {u'id': [u'Hash value is wrong length.']})

    patch_data['bids'][-1]['id'] = "00000000000000000000000000000000"

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Auction bids should be identical to the tender bids")

    patch_data['bids'][-1]['id'] = self.initial_bids[0]['id']

    for lot in self.initial_lots:
        response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot['id']), {'data': patch_data})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        tender = response.json['data']

    for x, y in enumerate(list(range(self.min_bids_number))[::-1]):
        self.assertNotEqual(tender["bids"][x]['lotValues'][0]['value']['amount'],
                            self.initial_bids[x]['lotValues'][0]['value']['amount'])
        self.assertEqual(tender["bids"][x]['lotValues'][0]['value']['amount'],
                         patch_data["bids"][y]['lotValues'][0]['value']['amount'])

    self.assertEqual('active.qualification', tender["status"])
    self.assertIn("tenderers", tender["bids"][0])
    self.assertIn("name", tender["bids"][0]["tenderers"][0])

    if len(self.initial_bids) > MaxAwards:
        self.assertEqual(len(tender['awards']), MaxAwards)
    else:
        self.assertLessEqual(len(tender['awards']), MaxAwards)

    for x in list(range(self.min_bids_number))[:MaxAwards]:
        self.assertEqual(tender["awards"][x]['bid_id'], patch_data["bids"][x]['id'])
        self.assertEqual(tender["awards"][x]['value']['amount'],
                         patch_data["bids"][x]['lotValues'][0]['value']['amount'])
        self.assertEqual(tender["awards"][x]['suppliers'], self.initial_bids[x]['tenderers'])

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't report auction results in current (active.qualification) tender status")


# TenderMultipleLotAuctionResourceTestMixin


def post_tender_lots_auction(self):
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': {}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't report auction results in current ({}) tender status".format(
                         self.forbidden_auction_actions_status))

    self.set_status('active.auction')

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id),
                                  {'data': {'bids': [{'invalid_field': 'invalid_value'}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'invalid_field': u'Rogue field'}, u'location': u'body', u'name': u'bids'}
    ])

    patch_data = {
        'bids': [
            {
                "id": self.initial_bids[-1]['id'],
                'lotValues': [
                    {
                        "value": {
                            "amount": 409,
                            "currency": "UAH",
                            "valueAddedTaxIncluded": True
                        }
                    }
                ]
            }
        ]
    }

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Number of auction results did not match the number of tender bids")

    update_patch_data(self, patch_data, key='lotValues', start=-2, interval=-1)

    patch_data['bids'][-1]['id'] = "some_id"

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], {u'id': [u'Hash value is wrong length.']})

    patch_data['bids'][-1]['id'] = "00000000000000000000000000000000"

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Auction bids should be identical to the tender bids")

    patch_data['bids'][-1]['id'] = self.initial_bids[0]['id']

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     [{"lotValues": ["Number of lots of auction results did not match the number of tender lots"]}])

    for bid in patch_data['bids']:
        bid['lotValues'] = [bid['lotValues'][0].copy() for i in self.initial_lots]

    patch_data['bids'][0]['lotValues'][1]['relatedLot'] = self.initial_bids[0]['lotValues'][0]['relatedLot']

    response = self.app.patch_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    # self.assertEqual(response.json['errors'][0]["description"], [{u'lotValues': [{u'relatedLot': [u'relatedLot should be one of lots of bid']}]}])
    self.assertEqual(response.json['errors'][0]["description"],
                     [{u'lotValues': [u"bids don't allow duplicated proposals"]}])

    patch_data['bids'][0]['lotValues'][1]['relatedLot'] = self.initial_bids[0]['lotValues'][1]['relatedLot']
    for lot in self.initial_lots:
        response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot['id']), {'data': patch_data})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        tender = response.json['data']

    if len(self.initial_bids) > MaxAwards:
        self.assertEqual(len(tender['awards']), MaxAwards * 2)  # init bids * 2lot (for each lot award)
    else:
        self.assertLessEqual(len(tender['awards']), MaxAwards * 2)

    for x, y in enumerate(list(range(self.min_bids_number))[::-1]):
        self.assertNotEqual(tender["bids"][x]['lotValues'][0]['value']['amount'],
                            self.initial_bids[x]['lotValues'][0]['value']['amount'])
        self.assertEqual(tender["bids"][x]['lotValues'][0]['value']['amount'],
                         patch_data["bids"][y]['lotValues'][0]['value']['amount'])

    self.assertEqual('active.qualification', tender["status"])
    self.assertIn("tenderers", tender["bids"][0])
    self.assertIn("name", tender["bids"][0]["tenderers"][0])

    for x in list(range(self.min_bids_number))[:MaxAwards]:
        self.assertEqual(tender["awards"][x]['bid_id'], patch_data["bids"][x]['id'])
        self.assertEqual(tender["awards"][x]['value']['amount'],
                         patch_data["bids"][x]['lotValues'][0]['value']['amount'])
        self.assertEqual(tender["awards"][x]['suppliers'], self.initial_bids[x]['tenderers'])

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"],
                     "Can't report auction results in current (active.qualification) tender status")
