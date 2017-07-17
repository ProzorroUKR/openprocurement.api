# -*- coding: utf-8 -*-
# TenderAuctionResourceTest


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
                    'yearlyPayments': 0.9,
                    'annualCostsReduction': 785.5,
                    'contractDuration': 10,
                    'amount': 730.044
                 },
            }
        ]
    }

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Number of auction results did not match the number of tender bids")

    patch_data['bids'].append({
        "value": {
            'yearlyPayments': 0.85,
            'annualCostsReduction': 798.1,
            'contractDuration': 10,
            'amount': 898.309
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
    self.assertNotEqual(tender["bids"][0]['value']['amount'], self.initial_bids[0]['value']['amount'])
    self.assertNotEqual(tender["bids"][1]['value']['amount'], self.initial_bids[1]['value']['amount'])
    self.assertEqual(tender["bids"][0]['value']['amount'], patch_data["bids"][1]['value']['amount'])
    self.assertEqual(tender["bids"][1]['value']['amount'], patch_data["bids"][0]['value']['amount'])
    self.assertEqual('active.qualification', tender["status"])
    self.assertIn("tenderers", tender["bids"][0])
    self.assertIn("name", tender["bids"][0]["tenderers"][0])
    # self.assertIn(tender["awards"][0]["id"], response.headers['Location'])

    # bid with higher amount is awarded because of reversed awardCriteria for esco.EU
    self.assertEqual(tender["awards"][0]['bid_id'], patch_data["bids"][1]['id'])
    self.assertEqual(tender["awards"][0]['value']['amount'], patch_data["bids"][1]['value']['amount'])
    self.assertEqual(tender["awards"][0]['suppliers'], self.initial_bids[0]['tenderers'])

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't report auction results in current (active.qualification) tender status")


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
                    'yearlyPayments': 0.9,
                    'annualCostsReduction': 785.5,
                    'contractDuration': 10,
                    'amount': 730.044
                 },
            },
            {
                "id": self.initial_bids[0]['id'],
                "value": {
                    'yearlyPayments': 0.85,
                    'annualCostsReduction': 798.1,
                    'contractDuration': 10,
                    'amount': 898.309
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


# TenderLotAuctionResourceTest


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
                            'yearlyPayments': 0.9,
                            'annualCostsReduction': 785.5,
                            'contractDuration': 10,
                            'amount': 730.044
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
                    'yearlyPayments': 0.85,
                    'annualCostsReduction': 798.1,
                    'contractDuration': 10,
                    'amount': 898.309
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

    self.assertNotEqual(tender["bids"][0]['lotValues'][0]['value']['amount'], self.initial_bids[0]['lotValues'][0]['value']['amount'])
    self.assertNotEqual(tender["bids"][1]['lotValues'][0]['value']['amount'], self.initial_bids[1]['lotValues'][0]['value']['amount'])
    self.assertEqual(tender["bids"][0]['lotValues'][0]['value']['amount'], patch_data["bids"][1]['lotValues'][0]['value']['amount'])
    self.assertEqual(tender["bids"][1]['lotValues'][0]['value']['amount'], patch_data["bids"][0]['lotValues'][0]['value']['amount'])
    self.assertEqual('active.qualification', tender["status"])
    self.assertIn("tenderers", tender["bids"][0])
    self.assertIn("name", tender["bids"][0]["tenderers"][0])
    # self.assertIn(tender["awards"][0]["id"], response.headers['Location'])

    # bid with higher amount is awarded because of reversed awardCriteria for esco.EU
    self.assertEqual(tender["awards"][0]['bid_id'], patch_data["bids"][1]['id'])
    self.assertEqual(tender["awards"][0]['value']['amount'], patch_data["bids"][1]['lotValues'][0]['value']['amount'])
    self.assertEqual(tender["awards"][0]['suppliers'], self.initial_bids[0]['tenderers'])

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't report auction results in current (active.qualification) tender status")

# TenderMultipleLotAuctionResourceTest


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
                            'yearlyPayments': 0.9,
                            'annualCostsReduction': 785.5,
                            'contractDuration': 10,
                            'amount': 730.044
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
                    'yearlyPayments': 0.85,
                    'annualCostsReduction': 798.1,
                    'contractDuration': 10,
                    'amount': 898.309
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

    self.assertNotEqual(tender["bids"][0]['lotValues'][0]['value']['amount'], self.initial_bids[0]['lotValues'][0]['value']['amount'])
    self.assertNotEqual(tender["bids"][1]['lotValues'][0]['value']['amount'], self.initial_bids[1]['lotValues'][0]['value']['amount'])
    self.assertEqual(tender["bids"][0]['lotValues'][0]['value']['amount'], patch_data["bids"][1]['lotValues'][0]['value']['amount'])
    self.assertEqual(tender["bids"][1]['lotValues'][0]['value']['amount'], patch_data["bids"][0]['lotValues'][0]['value']['amount'])
    self.assertEqual('active.qualification', tender["status"])
    self.assertIn("tenderers", tender["bids"][0])
    self.assertIn("name", tender["bids"][0]["tenderers"][0])
    # self.assertIn(tender["awards"][0]["id"], response.headers['Location'])

    # bid with higher amount is awarded because of reversed awardCriteria for esco.EU
    self.assertEqual(tender["awards"][0]['bid_id'], patch_data["bids"][1]['id'])
    self.assertEqual(tender["awards"][0]['value']['amount'], patch_data["bids"][1]['lotValues'][0]['value']['amount'])
    self.assertEqual(tender["awards"][0]['suppliers'], self.initial_bids[0]['tenderers'])

    response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id), {'data': patch_data}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't report auction results in current (active.qualification) tender status")
