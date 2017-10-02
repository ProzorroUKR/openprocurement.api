# -*- coding: utf-8 -*-
# TenderAuctionResourceTest
from datetime import timedelta
from openprocurement.api.utils import get_now


def get_tender_auction(self):
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(self.tender_id), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't get auction info in current ({}) tender status".format(self.forbidden_auction_actions_status))

    self.set_status('active.auction')

    response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    self.assertNotEqual(auction, self.initial_data)
    self.assertIn('dateModified', auction)
    self.assertIn('minimalStepPercentage', auction)
    self.assertIn('yearlyPaymentsPercentageRange', auction)
    self.assertIn('fundingKind', auction)
    self.assertIn('procurementMethodType', auction)
    self.assertIn('noticePublicationDate', auction)
    self.assertNotIn("procuringEntity", auction)
    self.assertNotIn("tenderers", auction["bids"][0])
    self.assertEqual(auction["bids"][0]['value']['amountPerformance'], self.initial_bids[0]['value']['amountPerformance'])
    self.assertEqual(auction["bids"][1]['value']['amountPerformance'], self.initial_bids[1]['value']['amountPerformance'])
    self.assertEqual(auction['procurementMethodType'], 'esco')

    response = self.app.get('/tenders/{}/auction?opt_jsonp=callback'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/javascript')
    self.assertIn('callback({"data": {"', response.body)

    response = self.app.get('/tenders/{}/auction?opt_pretty=1'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('{\n    "data": {\n        "', response.body)

    self.set_status('active.qualification')

    response = self.app.get('/tenders/{}/auction'.format(self.tender_id), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't get auction info in current (active.qualification) tender status")


def post_tender_auction(self):
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': {}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't report auction results in current ({}) tender status".format(self.forbidden_auction_actions_status))

    self.set_status('active.auction')

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': {'bids': [{'invalid_field': 'invalid_value'}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'invalid_field': u'Rogue field'}, u'location': u'body', u'name': u'bids'}
    ])

    patch_data = {
        'bids': [
            {
                "id": self.initial_bids[1]['id'],
                "value": {
                    'yearlyPaymentsPercentage': 0.9,
                    'contractDuration': {'years': 10},
                 },
            },
        ]
    }

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Number of auction results did not match the number of tender bids")

    patch_data['bids'].append({
        "value": {
            'yearlyPaymentsPercentage': 0.85,
            'contractDuration': {'years': 10},
        },
    })

    patch_data['bids'][1]['id'] = "some_id"

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], {u'id': [u'Hash value is wrong length.']})

    patch_data['bids'][1]['id'] = "00000000000000000000000000000000"
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Auction bids should be identical to the tender bids")

    patch_data['bids'][1]['id'] = self.initial_bids[0]['id']
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    tender = response.json['data']

    self.assertGreater(tender["bids"][0]['value']['amountPerformance'], 10)
    self.assertLess(tender["bids"][0]['value']['amountPerformance'], 1500)
    self.assertGreater(tender["bids"][0]['value']['amount'], 500)
    self.assertLess(tender["bids"][0]['value']['amount'], 15000)
    self.assertEqual(tender["bids"][0]['value']['yearlyPaymentsPercentage'], patch_data["bids"][1]['value']['yearlyPaymentsPercentage'])
    self.assertEqual(tender["bids"][1]['value']['yearlyPaymentsPercentage'], patch_data["bids"][0]['value']['yearlyPaymentsPercentage'])
    self.assertEqual(tender["bids"][0]['value']['contractDuration']['years'], patch_data["bids"][1]['value']['contractDuration']['years'])
    self.assertEqual(tender["bids"][1]['value']['contractDuration']['years'], patch_data["bids"][0]['value']['contractDuration']['years'])
    self.assertEqual('active.qualification', tender["status"])
    self.assertIn("tenderers", tender["bids"][0])
    self.assertIn("name", tender["bids"][0]["tenderers"][0])
    # self.assertIn(tender["awards"][0]["id"], response.headers['Location'])

    # bid with higher amountPerformance is awarded because of reversed awardCriteria for esco.EUf
    self.assertEqual(tender["awards"][0]['bid_id'], tender["bids"][0]['id'])
    self.assertEqual(tender["awards"][0]['value']['amountPerformance'], tender["bids"][0]['value']['amountPerformance'])
    self.assertEqual(tender["awards"][0]['value']['amount'], tender["bids"][0]['value']['amount'])
    self.assertEqual(tender["awards"][0]['suppliers'], self.initial_bids[0]['tenderers'])

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't report auction results in current (active.qualification) tender status")


# TenderAuctionFieldsTest


def auction_check_NBUdiscountRate(self):
    self.app.authorization = ('Basic', ('auction', ''))
    self.set_status('active.auction')

    response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['NBUdiscountRate'], 0.22)

    # try to patch NBUdiscountRate in tender
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"NBUdiscountRate": 0.44}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["location"], "url")
    self.assertEqual(response.json['errors'][0]["name"], "permission")
    self.assertEqual(response.json['errors'][0]["description"], "Forbidden")

    # try to patch NBUdiscountRate in auction data, but it should not change
    response = self.app.patch_json('/tenders/{}/auction'.format(self.tender_id), {'data': {"NBUdiscountRate": 0.44}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['NBUdiscountRate'], 0.22)

    patch_data = {
        'bids': [
            {
                "id": self.initial_bids[1]['id'],
                "value": {
                    'yearlyPaymentsPercentage': 0.9,
                    'contractDuration': {'years': 10},
                 },
            },
            {
                "id": self.initial_bids[0]['id'],
                "value": {
                    'yearlyPaymentsPercentage': 0.85,
                    'contractDuration': {'years': 10},
                },
            },
        ],
        'NBUdiscountRate': 0.33,
    }

    # try to change NBUdiscountRate with posting auction results, but it should not change
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['NBUdiscountRate'], 0.22)


def auction_check_noticePublicationDate(self):
    self.app.authorization = ('Basic', ('auction', ''))
    self.set_status('active.auction')

    response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertIn('noticePublicationDate', response.json['data'])
    publication_date = response.json['data']['noticePublicationDate']

    # try to patch noticePublicationDate in tender
    response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {"noticePublicationDate": get_now().isoformat()}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["location"], "url")
    self.assertEqual(response.json['errors'][0]["name"], "permission")
    self.assertEqual(response.json['errors'][0]["description"], "Forbidden")

    # try to patch noticePublicationDate in auction data, but it should not change
    response = self.app.patch_json('/tenders/{}/auction'.format(self.tender_id), {'data': {"noticePublicationDate": get_now().isoformat()}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['noticePublicationDate'], publication_date)

    patch_data = {
        'bids': [
            {
                "id": self.initial_bids[1]['id'],
                "value": {
                    'yearlyPaymentsPercentage': 0.9,
                    'contractDuration': {'years': 10},
                 },
            },
            {
                "id": self.initial_bids[0]['id'],
                "value": {
                    'yearlyPaymentsPercentage': 0.85,
                    'contractDuration': {'years': 10},
                },
            },
        ],
        'noticePublicationDate': get_now().isoformat(),
    }

    # try to change noticePublicationDate with posting auction results, but it should not change
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['noticePublicationDate'], publication_date)


# TenderSameValueAuctionResourceTest


def post_tender_auction_not_changed(self):
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': {'bids': self.initial_bids}})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    tender = response.json['data']
    self.assertEqual('active.qualification', tender["status"])
    self.assertEqual(tender["awards"][0]['bid_id'], self.initial_bids[0]['id'])
    self.assertEqual(tender["awards"][0]['value']['amountPerformance'], self.initial_bids[0]['value']['amountPerformance'])
    self.assertEqual(tender["awards"][0]['value']['amount'], self.initial_bids[0]['value']['amount'])
    self.assertEqual(tender["awards"][0]['suppliers'], self.initial_bids[0]['tenderers'])


def post_tender_auction_reversed(self):
    self.app.authorization = ('Basic', ('auction', ''))
    now = get_now()
    patch_data = {
        'bids': [
            {
                "id": b['id'],
                "date": (now - timedelta(seconds=i)).isoformat(),
                "value": b['value']
            }
            for i, b in enumerate(self.initial_bids)
        ]
    }

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    tender = response.json['data']
    self.assertEqual('active.qualification', tender["status"])
    self.assertEqual(tender["awards"][0]['bid_id'], self.initial_bids[2]['id'])
    self.assertEqual(tender["awards"][0]['value']['amountPerformance'], self.initial_bids[2]['value']['amountPerformance'])
    self.assertEqual(tender["awards"][0]['value']['amount'], self.initial_bids[2]['value']['amount'])
    self.assertEqual(tender["awards"][0]['suppliers'], self.initial_bids[2]['tenderers'])


# TenderLotAuctionResourceTest


def get_tender_lot_auction(self):
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(self.tender_id), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't get auction info in current ({}) tender status".format(self.forbidden_auction_actions_status))

    self.set_status('active.auction')

    response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    self.assertNotEqual(auction, self.initial_data)
    self.assertIn('dateModified', auction)
    self.assertIn('lots', auction)
    self.assertIn('yearlyPaymentsPercentageRange', auction)
    self.assertIn('fundingKind', auction)
    self.assertIn('yearlyPaymentsPercentageRange', auction['lots'][0])
    self.assertIn('fundingKind', auction['lots'][0])
    self.assertNotIn("procuringEntity", auction)
    self.assertNotIn("tenderers", auction["bids"][0])
    self.assertEqual(auction["bids"][0]['lotValues'][0]['value']['amountPerformance'], self.initial_bids[0]['lotValues'][0]['value']['amountPerformance'])
    self.assertEqual(auction["bids"][1]['lotValues'][0]['value']['amountPerformance'], self.initial_bids[1]['lotValues'][0]['value']['amountPerformance'])

    self.set_status('active.qualification')

    response = self.app.get('/tenders/{}/auction'.format(self.tender_id), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't get auction info in current (active.qualification) tender status")


def post_tender_lot_auction(self):
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': {}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't report auction results in current ({}) tender status".format(self.forbidden_auction_actions_status))

    self.set_status('active.auction')

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': {'bids': [{'invalid_field': 'invalid_value'}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'invalid_field': u'Rogue field'}, u'location': u'body', u'name': u'bids'}
    ])

    patch_data = {
        'bids': [
            {
                "id": self.initial_bids[1]['id'],
                "lotValues": [
                    {
                        "value": {
                            'yearlyPaymentsPercentage': 0.9,
                            'contractDuration': {'years': 10}
                        }
                    }
                ]
            }
        ]
    }

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Number of auction results did not match the number of tender bids")

    patch_data['bids'].append({
        'lotValues': [
            {
                "value": {
                    'yearlyPaymentsPercentage': 0.85,
                    'contractDuration': {'years': 10},
                }
            }
        ]
    })

    patch_data['bids'][1]['id'] = "some_id"

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], {u'id': [u'Hash value is wrong length.']})

    patch_data['bids'][1]['id'] = "00000000000000000000000000000000"

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Auction bids should be identical to the tender bids")

    patch_data['bids'][1]['id'] = self.initial_bids[0]['id']

    for lot in self.initial_lots:
        response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot['id']), {'data': patch_data})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        tender = response.json['data']

    self.assertGreater(tender["bids"][0]['lotValues'][0]['value']['amountPerformance'], 10)
    self.assertLess(tender["bids"][0]['lotValues'][0]['value']['amountPerformance'], 1500)
    self.assertGreater(tender["bids"][0]['lotValues'][0]['value']['amount'], 500)
    self.assertLess(tender["bids"][0]['lotValues'][0]['value']['amount'], 15000)
    self.assertEqual(tender["bids"][0]['lotValues'][0]['value']['yearlyPaymentsPercentage'], patch_data["bids"][1]['lotValues'][0]['value']['yearlyPaymentsPercentage'])
    self.assertEqual(tender["bids"][1]['lotValues'][0]['value']['yearlyPaymentsPercentage'], patch_data["bids"][0]['lotValues'][0]['value']['yearlyPaymentsPercentage'])
    self.assertEqual(tender["bids"][0]['lotValues'][0]['value']['contractDuration']['years'], patch_data["bids"][1]['lotValues'][0]['value']['contractDuration']['years'])
    self.assertEqual(tender["bids"][1]['lotValues'][0]['value']['contractDuration']['years'], patch_data["bids"][0]['lotValues'][0]['value']['contractDuration']['years'])
    self.assertEqual('active.qualification', tender["status"])
    self.assertIn("tenderers", tender["bids"][0])
    self.assertIn("name", tender["bids"][0]["tenderers"][0])
    # self.assertIn(tender["awards"][0]["id"], response.headers['Location'])

    # bid with higher amountPerformance is awarded because of reversed awardCriteria for esco.EU
    self.assertEqual(tender["awards"][0]['bid_id'], tender["bids"][0]['id'])
    self.assertEqual(tender["awards"][0]['value']['amountPerformance'], tender["bids"][0]['lotValues'][0]['value']['amountPerformance'])
    self.assertEqual(tender["awards"][0]['value']['amount'], tender["bids"][0]['lotValues'][0]['value']['amount'])
    self.assertEqual(tender["awards"][0]['suppliers'], self.initial_bids[0]['tenderers'])

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't report auction results in current (active.qualification) tender status")

# TenderMultipleLotAuctionResourceTest


def get_tender_lots_auction(self):
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(self.tender_id), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't get auction info in current ({}) tender status".format(self.forbidden_auction_actions_status))

    self.set_status('active.auction')

    response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    self.assertNotEqual(auction, self.initial_data)
    self.assertIn('dateModified', auction)
    self.assertIn('lots', auction)
    self.assertIn('yearlyPaymentsPercentageRange', auction)
    self.assertIn('fundingKind', auction)
    self.assertIn('yearlyPaymentsPercentageRange', auction['lots'][0])
    self.assertIn('fundingKind', auction['lots'][0])
    self.assertIn('items', auction)
    self.assertNotIn("procuringEntity", auction)
    self.assertNotIn("tenderers", auction["bids"][0])
    self.assertEqual(auction["bids"][0]['lotValues'][0]['value']['amountPerformance'], self.initial_bids[0]['lotValues'][0]['value']['amountPerformance'])
    self.assertEqual(auction["bids"][1]['lotValues'][0]['value']['amountPerformance'], self.initial_bids[1]['lotValues'][0]['value']['amountPerformance'])

    self.set_status('active.qualification')

    response = self.app.get('/tenders/{}/auction'.format(self.tender_id), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't get auction info in current (active.qualification) tender status")


def post_tender_lots_auction(self):
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': {}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't report auction results in current ({}) tender status".format(self.forbidden_auction_actions_status))

    self.set_status('active.auction')

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': {'bids': [{'invalid_field': 'invalid_value'}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'invalid_field': u'Rogue field'}, u'location': u'body', u'name': u'bids'}
    ])

    patch_data = {
        'bids': [
            {
                "id": self.initial_bids[1]['id'],
                "lotValues": [
                    {
                        "value": {
                            'yearlyPaymentsPercentage': 0.9,
                            'contractDuration': {'years': 10},
                        }
                    }
                ]
            }
        ]
    }

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Number of auction results did not match the number of tender bids")

    patch_data['bids'].append({
        'lotValues': [
            {
                "value": {
                    'yearlyPaymentsPercentage': 0.85,
                    'contractDuration': {'years': 10},
                }
            }
        ]
    })

    patch_data['bids'][1]['id'] = "some_id"

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], {u'id': [u'Hash value is wrong length.']})

    patch_data['bids'][1]['id'] = "00000000000000000000000000000000"

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Auction bids should be identical to the tender bids")

    patch_data['bids'][1]['id'] = self.initial_bids[0]['id']

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], [{"lotValues": ["Number of lots of auction results did not match the number of tender lots"]}])

    for bid in patch_data['bids']:
        bid['lotValues'] = [bid['lotValues'][0].copy() for i in self.initial_lots]

    patch_data['bids'][0]['lotValues'][1]['relatedLot'] = self.initial_bids[0]['lotValues'][0]['relatedLot']

    response = self.app.patch_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    #self.assertEqual(response.json['errors'][0]["description"], [{u'lotValues': [{u'relatedLot': [u'relatedLot should be one of lots of bid']}]}])
    self.assertEqual(response.json['errors'][0]["description"], [{u'lotValues': [u"bids don't allow duplicated proposals"]}])

    patch_data['bids'][0]['lotValues'][1]['relatedLot'] = self.initial_bids[0]['lotValues'][1]['relatedLot']

    for lot in self.initial_lots:
        response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot['id']), {'data': patch_data})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        tender = response.json['data']

    self.assertGreater(tender["bids"][0]['lotValues'][0]['value']['amountPerformance'], 10)
    self.assertLess(tender["bids"][0]['lotValues'][0]['value']['amountPerformance'], 1500)
    self.assertGreater(tender["bids"][0]['lotValues'][0]['value']['amount'], 500)
    self.assertLess(tender["bids"][0]['lotValues'][0]['value']['amount'], 15000)
    self.assertEqual(tender["bids"][0]['lotValues'][0]['value']['yearlyPaymentsPercentage'], patch_data["bids"][1]['lotValues'][0]['value']['yearlyPaymentsPercentage'])
    self.assertEqual(tender["bids"][1]['lotValues'][0]['value']['yearlyPaymentsPercentage'], patch_data["bids"][0]['lotValues'][0]['value']['yearlyPaymentsPercentage'])
    self.assertEqual(tender["bids"][0]['lotValues'][0]['value']['contractDuration']['years'], patch_data["bids"][1]['lotValues'][0]['value']['contractDuration']['years'])
    self.assertEqual(tender["bids"][1]['lotValues'][0]['value']['contractDuration']['years'], patch_data["bids"][0]['lotValues'][0]['value']['contractDuration']['years'])
    self.assertEqual('active.qualification', tender["status"])
    self.assertIn("tenderers", tender["bids"][0])
    self.assertIn("name", tender["bids"][0]["tenderers"][0])
    # self.assertIn(tender["awards"][0]["id"], response.headers['Location'])

    # bid with higher amountPerformance is awarded because of reversed awardCriteria for esco.EU
    self.assertEqual(tender["awards"][0]['bid_id'], tender["bids"][0]['id'])
    self.assertEqual(tender["awards"][0]['value']['amountPerformance'], tender["bids"][0]['lotValues'][0]['value']['amountPerformance'])
    self.assertEqual(tender["awards"][0]['value']['amount'], tender["bids"][0]['lotValues'][0]['value']['amount'])
    self.assertEqual(tender["awards"][0]['suppliers'], self.initial_bids[0]['tenderers'])

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't report auction results in current (active.qualification) tender status")


# TenderFeaturesAuctionResourceTest


def get_tender_auction_feature(self):
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(self.tender_id), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't get auction info in current ({}) tender status".format(self.forbidden_auction_actions_status))

    self.set_status('active.auction')
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    self.assertNotEqual(auction, self.initial_data)
    self.assertIn('dateModified', auction)
    self.assertNotIn("procuringEntity", auction)
    self.assertIn('yearlyPaymentsPercentageRange', auction)
    self.assertIn('fundingKind', auction)
    self.assertNotIn("tenderers", auction["bids"][0])
    self.assertEqual(auction["bids"][0]['value']['amountPerformance'], self.initial_bids[0]['value']['amountPerformance'])
    self.assertEqual(auction["bids"][1]['value']['amountPerformance'], self.initial_bids[1]['value']['amountPerformance'])
    self.assertIn('features', auction)
    self.assertIn('parameters', auction["bids"][0])

    self.set_status('active.qualification')

    response = self.app.get('/tenders/{}/auction'.format(self.tender_id), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't get auction info in current (active.qualification) tender status")


def post_tender_auction_feature(self):
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': {}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't report auction results in current ({}) tender status".format(self.forbidden_auction_actions_status))

    self.set_status('active.auction')

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': {'bids': [{'invalid_field': 'invalid_value'}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'invalid_field': u'Rogue field'}, u'location': u'body', u'name': u'bids'}
    ])

    patch_data = {
        'bids': [
            {
                "id": self.initial_bids[1]['id'],
                "value": {
                    'yearlyPaymentsPercentage': 0.9,
                    'contractDuration': {'years': 10},
                 },
            },
        ]
    }

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Number of auction results did not match the number of tender bids")

    patch_data['bids'].append({
        "value": {
            'yearlyPaymentsPercentage': 0.9,
            'contractDuration': {'years': 10},
        },
    })

    patch_data['bids'][1]['id'] = "some_id"

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], {u'id': [u'Hash value is wrong length.']})

    patch_data['bids'][1]['id'] = "00000000000000000000000000000000"
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Auction bids should be identical to the tender bids")

    patch_data['bids'][1]['id'] = self.initial_bids[0]['id']
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    tender = response.json['data']

    self.assertGreater(tender["bids"][0]['value']['amountPerformance'], 10)
    self.assertLess(tender["bids"][0]['value']['amountPerformance'], 1500)
    self.assertGreater(tender["bids"][0]['value']['amount'], 500)
    self.assertLess(tender["bids"][0]['value']['amount'], 15000)
    self.assertEqual(tender["bids"][0]['value']['yearlyPaymentsPercentage'], patch_data["bids"][1]['value']['yearlyPaymentsPercentage'])
    self.assertEqual(tender["bids"][1]['value']['yearlyPaymentsPercentage'], patch_data["bids"][0]['value']['yearlyPaymentsPercentage'])
    self.assertEqual(tender["bids"][0]['value']['contractDuration']['years'], patch_data["bids"][1]['value']['contractDuration']['years'])
    self.assertEqual(tender["bids"][1]['value']['contractDuration']['years'], patch_data["bids"][0]['value']['contractDuration']['years'])
    self.assertEqual('active.qualification', tender["status"])
    self.assertIn("tenderers", tender["bids"][0])
    self.assertIn("name", tender["bids"][0]["tenderers"][0])
    # self.assertIn(tender["awards"][0]["id"], response.headers['Location'])

    # bids have same amountPerformance, but bid with better parameters awarded
    self.assertEqual(tender["awards"][0]['bid_id'], tender["bids"][1]['id'])
    self.assertEqual(tender["awards"][0]['value']['amountPerformance'], tender["bids"][1]['value']['amountPerformance'])
    self.assertEqual(tender["awards"][0]['value']['amount'], tender["bids"][1]['value']['amount'])
    self.assertEqual(tender["awards"][0]['suppliers'], self.initial_bids[1]['tenderers'])

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't report auction results in current (active.qualification) tender status")


# TenderFeaturesLotAuctionResourceTest


def get_tender_lot_auction_feature(self):
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(self.tender_id), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't get auction info in current ({}) tender status".format(self.forbidden_auction_actions_status))

    self.set_status('active.auction')

    response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    self.assertNotEqual(auction, self.initial_data)
    self.assertIn('dateModified', auction)
    self.assertIn('lots', auction)
    self.assertIn('yearlyPaymentsPercentageRange', auction)
    self.assertIn('fundingKind', auction)
    self.assertIn('yearlyPaymentsPercentageRange', auction['lots'][0])
    self.assertIn('fundingKind', auction['lots'][0])
    self.assertNotIn("procuringEntity", auction)
    self.assertNotIn("tenderers", auction["bids"][0])
    self.assertEqual(auction["bids"][0]['lotValues'][0]['value']['amountPerformance'], self.initial_bids[0]['lotValues'][0]['value']['amountPerformance'])
    self.assertEqual(auction["bids"][1]['lotValues'][0]['value']['amountPerformance'], self.initial_bids[1]['lotValues'][0]['value']['amountPerformance'])
    self.assertIn('features', auction)
    self.assertIn('parameters', auction["bids"][0])

    self.set_status('active.qualification')

    response = self.app.get('/tenders/{}/auction'.format(self.tender_id), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't get auction info in current (active.qualification) tender status")


def post_tender_lot_auction_feature(self):
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': {}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't report auction results in current ({}) tender status".format(self.forbidden_auction_actions_status))

    self.set_status('active.auction')

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': {'bids': [{'invalid_field': 'invalid_value'}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'invalid_field': u'Rogue field'}, u'location': u'body', u'name': u'bids'}
    ])

    patch_data = {
        'bids': [
            {
                "id": self.initial_bids[1]['id'],
                "lotValues": [
                    {
                        "value": {
                            'yearlyPaymentsPercentage': 0.9,
                            'contractDuration': {'years': 10}
                        }
                    }
                ]
            }
        ]
    }

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Number of auction results did not match the number of tender bids")

    patch_data['bids'].append({
        'lotValues': [
            {
                "value": {
                    'yearlyPaymentsPercentage': 0.9,
                    'contractDuration': {'years': 10},
                }
            }
        ]
    })

    patch_data['bids'][1]['id'] = "some_id"

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], {u'id': [u'Hash value is wrong length.']})

    patch_data['bids'][1]['id'] = "00000000000000000000000000000000"

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Auction bids should be identical to the tender bids")

    patch_data['bids'][1]['id'] = self.initial_bids[0]['id']

    for lot in self.initial_lots:
        response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot['id']), {'data': patch_data})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        tender = response.json['data']

    self.assertGreater(tender["bids"][0]['lotValues'][0]['value']['amountPerformance'], 10)
    self.assertLess(tender["bids"][0]['lotValues'][0]['value']['amountPerformance'], 1500)
    self.assertGreater(tender["bids"][0]['lotValues'][0]['value']['amount'], 500)
    self.assertLess(tender["bids"][0]['lotValues'][0]['value']['amount'], 15000)
    self.assertEqual(tender["bids"][0]['lotValues'][0]['value']['yearlyPaymentsPercentage'], patch_data["bids"][1]['lotValues'][0]['value']['yearlyPaymentsPercentage'])
    self.assertEqual(tender["bids"][1]['lotValues'][0]['value']['yearlyPaymentsPercentage'], patch_data["bids"][0]['lotValues'][0]['value']['yearlyPaymentsPercentage'])
    self.assertEqual(tender["bids"][0]['lotValues'][0]['value']['contractDuration']['years'], patch_data["bids"][1]['lotValues'][0]['value']['contractDuration']['years'])
    self.assertEqual(tender["bids"][1]['lotValues'][0]['value']['contractDuration']['years'], patch_data["bids"][0]['lotValues'][0]['value']['contractDuration']['years'])
    self.assertEqual('active.qualification', tender["status"])
    self.assertIn("tenderers", tender["bids"][0])
    self.assertIn("name", tender["bids"][0]["tenderers"][0])
    # self.assertIn(tender["awards"][0]["id"], response.headers['Location'])

    # bids have same amountPerformance, but bid with better parameters awarded
    self.assertEqual(tender["awards"][0]['bid_id'], tender["bids"][1]['id'])
    self.assertEqual(tender["awards"][0]['value']['amountPerformance'], tender["bids"][1]['lotValues'][0]['value']['amountPerformance'])
    self.assertEqual(tender["awards"][0]['value']['amount'], tender["bids"][1]['lotValues'][0]['value']['amount'])
    self.assertEqual(tender["awards"][0]['suppliers'], self.initial_bids[1]['tenderers'])

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't report auction results in current (active.qualification) tender status")


# TenderFeaturesMultipleLotAuctionResourceTest


def get_tender_lots_auction_feature(self):
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.get('/tenders/{}/auction'.format(self.tender_id), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't get auction info in current ({}) tender status".format(self.forbidden_auction_actions_status))

    self.set_status('active.auction')

    response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    auction = response.json['data']
    self.assertNotEqual(auction, self.initial_data)
    self.assertIn('dateModified', auction)
    self.assertIn('lots', auction)
    self.assertIn('yearlyPaymentsPercentageRange', auction)
    self.assertIn('fundingKind', auction)
    self.assertIn('yearlyPaymentsPercentageRange', auction['lots'][0])
    self.assertIn('fundingKind', auction['lots'][0])
    self.assertIn('items', auction)
    self.assertNotIn("procuringEntity", auction)
    self.assertNotIn("tenderers", auction["bids"][0])
    self.assertEqual(auction["bids"][0]['lotValues'][0]['value']['amountPerformance'], self.initial_bids[0]['lotValues'][0]['value']['amountPerformance'])
    self.assertEqual(auction["bids"][1]['lotValues'][0]['value']['amountPerformance'], self.initial_bids[1]['lotValues'][0]['value']['amountPerformance'])
    self.assertIn('features', auction)
    self.assertIn('parameters', auction["bids"][0])

    self.set_status('active.qualification')

    response = self.app.get('/tenders/{}/auction'.format(self.tender_id), status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't get auction info in current (active.qualification) tender status")


def post_tender_lots_auction_feature(self):
    self.app.authorization = ('Basic', ('auction', ''))
    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': {}}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't report auction results in current ({}) tender status".format(self.forbidden_auction_actions_status))

    self.set_status('active.auction')

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': {'bids': [{'invalid_field': 'invalid_value'}]}}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': {u'invalid_field': u'Rogue field'}, u'location': u'body', u'name': u'bids'}
    ])

    patch_data = {
        'bids': [
            {
                "id": self.initial_bids[1]['id'],
                "lotValues": [
                    {
                        "value": {
                            'yearlyPaymentsPercentage': 0.9,
                            'contractDuration': {'years': 10},
                        }
                    }
                ]
            }
        ]
    }

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Number of auction results did not match the number of tender bids")

    patch_data['bids'].append({
        'lotValues': [
            {
                "value": {
                    'yearlyPaymentsPercentage': 0.9,
                    'contractDuration': {'years': 10},
                }
            }
        ]
    })

    patch_data['bids'][1]['id'] = "some_id"

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], {u'id': [u'Hash value is wrong length.']})

    patch_data['bids'][1]['id'] = "00000000000000000000000000000000"

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Auction bids should be identical to the tender bids")

    patch_data['bids'][1]['id'] = self.initial_bids[0]['id']

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], [{"lotValues": ["Number of lots of auction results did not match the number of tender lots"]}])

    for bid in patch_data['bids']:
        bid['lotValues'] = [bid['lotValues'][0].copy() for i in self.initial_lots]

    patch_data['bids'][0]['lotValues'][1]['relatedLot'] = self.initial_bids[0]['lotValues'][0]['relatedLot']

    response = self.app.patch_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    #self.assertEqual(response.json['errors'][0]["description"], [{u'lotValues': [{u'relatedLot': [u'relatedLot should be one of lots of bid']}]}])
    self.assertEqual(response.json['errors'][0]["description"], [{u'lotValues': [u"bids don't allow duplicated proposals"]}])

    patch_data['bids'][0]['lotValues'][1]['relatedLot'] = self.initial_bids[0]['lotValues'][1]['relatedLot']

    for lot in self.initial_lots:
        response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot['id']), {'data': patch_data})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        tender = response.json['data']

    self.assertGreater(tender["bids"][0]['lotValues'][0]['value']['amountPerformance'], 10)
    self.assertLess(tender["bids"][0]['lotValues'][0]['value']['amountPerformance'], 1500)
    self.assertGreater(tender["bids"][0]['lotValues'][0]['value']['amount'], 500)
    self.assertLess(tender["bids"][0]['lotValues'][0]['value']['amount'], 15000)
    self.assertEqual(tender["bids"][0]['lotValues'][0]['value']['yearlyPaymentsPercentage'], patch_data["bids"][1]['lotValues'][0]['value']['yearlyPaymentsPercentage'])
    self.assertEqual(tender["bids"][1]['lotValues'][0]['value']['yearlyPaymentsPercentage'], patch_data["bids"][0]['lotValues'][0]['value']['yearlyPaymentsPercentage'])
    self.assertEqual(tender["bids"][0]['lotValues'][0]['value']['contractDuration']['years'], patch_data["bids"][1]['lotValues'][0]['value']['contractDuration']['years'])
    self.assertEqual(tender["bids"][1]['lotValues'][0]['value']['contractDuration']['years'], patch_data["bids"][0]['lotValues'][0]['value']['contractDuration']['years'])
    self.assertEqual('active.qualification', tender["status"])
    self.assertIn("tenderers", tender["bids"][0])
    self.assertIn("name", tender["bids"][0]["tenderers"][0])
    # self.assertIn(tender["awards"][0]["id"], response.headers['Location'])

    # bid have same amountPerformance, but bid with better parameters awarded
    self.assertEqual(tender["awards"][0]['bid_id'], tender["bids"][1]['id'])
    self.assertEqual(tender["awards"][0]['value']['amountPerformance'], tender["bids"][0]['lotValues'][1]['value']['amountPerformance'])
    self.assertEqual(tender["awards"][0]['value']['amount'], tender["bids"][1]['lotValues'][0]['value']['amount'])
    self.assertEqual(tender["awards"][0]['suppliers'], self.initial_bids[1]['tenderers'])

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't report auction results in current (active.qualification) tender status")
