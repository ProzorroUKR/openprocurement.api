# -*- coding: utf-8 -*-
import datetime

import json

import os
from copy import deepcopy

from openprocurement.tender.open.tests.tender import BaseTenderUAWebTest
from openprocurement.tender.core.tests.base import (
    test_exclusion_criteria,
    test_language_criteria,
)
from tests.base.constants import (
    DOCS_URL,
    AUCTIONS_URL,
)
from tests.base.test import (
    DumpsWebTestApp,
    MockWebTestMixin,
)
from tests.base.data import (
    test_docs_tender_open,
    test_docs_bid2,
    test_docs_lots,
    test_docs_bid,
)

TARGET_DIR = 'docs/source/tendering/config/http/'
TARGET_JSON_DIR = 'docs/source/tendering/config/json/'


class TenderHasAuctionResourceTest(BaseTenderUAWebTest, MockWebTestMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_docs_tender_open
    docservice = True
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL

    whitelist = ('/openprocurement/.*models.*', )
    blacklist = ('/tests/.*\.py',)

    def setUp(self):
        super(TenderHasAuctionResourceTest, self).setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super(TenderHasAuctionResourceTest, self).tearDown()

    def test_docs_has_auction_true(self):
        request_path = '/tenders?opt_pretty=1'

        config = deepcopy(self.initial_config)
        config["hasAuction"] = True

        test_tender_data = deepcopy(test_docs_tender_open)
        test_lots = deepcopy(test_docs_lots)
        test_lots[0]['value'] = test_tender_data['value']
        test_lots[0]['minimalStep'] = test_tender_data['minimalStep']
        test_lots[1]['value'] = test_tender_data['value']
        test_lots[1]['minimalStep'] = test_tender_data['minimalStep']

        #### Creating tender

        with open(TARGET_DIR + 'has-auction-true-tender-post.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': test_tender_data, 'config': config}
            )
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        self.app.authorization = ('Basic', ('broker', ''))

        # add lots
        with open(TARGET_DIR + 'has-auction-true-tender-add-lot.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                {'data': test_lots[0]}
            )
            self.assertEqual(response.status, '201 Created')
            lot_id1 = response.json['data']['id']

        response = self.app.post_json(
            '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
            {'data': test_lots[1]}
        )
        self.assertEqual(response.status, '201 Created')
        lot2 = response.json['data']
        lot_id2 = lot2['id']

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = lot_id1
        items[1]["relatedLot"] = lot_id2
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
            {"data": {"items": items}}
        )
        self.assertEqual(response.status, '200 OK')

        self.add_criteria(tender_id, owner_token)
        self.activate_tender(tender_id, owner_token)
        bid1_id, bid1_token, bid2_id, bid2_token = self.register_bids(
            tender_id, owner_token, lot_id1, lot_id2
        )

        #### Auction
        self.tick(datetime.timedelta(days=30))
        self.check_chronograph()

        self.app.authorization = ('Basic', ('auction', ''))
        auction1_url = '{}/tenders/{}_{}'.format(self.auctions_url, self.tender_id, lot_id1)
        auction2_url = '{}/tenders/{}_{}'.format(self.auctions_url, self.tender_id, lot_id2)
        patch_data = {
            'lots': [
                {
                    'id': lot_id1,
                    'auctionUrl': auction1_url,
                },
                {
                    'id': lot_id2,
                    'auctionUrl': auction2_url,
                },
            ],
            'bids': [{
                "id": bid1_id,
                "lotValues": [
                    {"participationUrl": '{}?key_for_bid={}'.format(auction1_url, bid1_id)},
                    {"participationUrl": '{}?key_for_bid={}'.format(auction2_url, bid1_id)},
                ]
            }, {
                "id": bid2_id,
                "lotValues": [
                    {"participationUrl": '{}?key_for_bid={}'.format(auction1_url, bid2_id)},
                    {"participationUrl": '{}?key_for_bid={}'.format(auction2_url, bid2_id)},
                ]
            }]
        }
        response = self.app.patch_json(
            '/tenders/{}/auction/{}?acc_token={}'.format(self.tender_id, lot_id1, owner_token),
            {'data': patch_data}
        )
        self.assertEqual(response.status, '200 OK')
        response = self.app.patch_json(
            '/tenders/{}/auction/{}?acc_token={}'.format(self.tender_id, lot_id2, owner_token),
            {'data': patch_data}
        )
        self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        #### Confirming qualification
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        response = self.app.post_json(
            '/tenders/{}/auction/{}'.format(self.tender_id, lot_id1),
            {
                'data': {
                    'bids': [
                        {
                            "id": b["id"], "lotValues": [
                            {"value": l["value"], "relatedLot": l["relatedLot"]}
                            for l in b["lotValues"]
                        ]
                    } for b in auction_bids_data]
                }
            }
        )
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        response = self.app.post_json(
            '/tenders/{}/auction/{}'.format(self.tender_id, lot_id2),
            {
                'data': {
                    'bids': [
                        {
                            "id": b["id"], "lotValues": [
                            {"value": l["value"], "relatedLot": l["relatedLot"]}
                            for l in b["lotValues"]
                        ]
                    } for b in auction_bids_data]
                }
            }
        )

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        with open(TARGET_JSON_DIR + 'has-auction-false-tender-check.json', 'w') as file_json:
            file_json.write(json.dumps(response.json, indent=4, sort_keys=True))


        self.complete_tender(tender_id, owner_token)

        with open(TARGET_DIR + 'has-auction-true-tender-complete.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_JSON_DIR + 'has-auction-true-tender-complete.json', 'w') as file_json:
            file_json.write(json.dumps(response.json, indent=4, sort_keys=True))

    def test_docs_has_auction_false(self):
        request_path = '/tenders?opt_pretty=1'

        config = deepcopy(self.initial_config)
        config["hasAuction"] = False

        test_tender_data = deepcopy(test_docs_tender_open)
        del test_tender_data['minimalStep']
        test_lots = deepcopy(test_docs_lots)
        test_lots[0]['value'] = test_tender_data['value']
        test_lots[1]['value'] = test_tender_data['value']

        #### Creating tender

        with open(TARGET_DIR + 'has-auction-false-tender-post.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': test_tender_data, 'config': config}
            )
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        self.app.authorization = ('Basic', ('broker', ''))

        # add lots
        with open(TARGET_DIR + 'has-auction-false-tender-add-lot.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                {'data': test_lots[0]}
            )
            self.assertEqual(response.status, '201 Created')
            lot_id1 = response.json['data']['id']

        response = self.app.post_json(
            '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
            {'data': test_lots[1]}
        )
        self.assertEqual(response.status, '201 Created')
        lot2 = response.json['data']
        lot_id2 = lot2['id']

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = lot_id1
        items[1]["relatedLot"] = lot_id2
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
            {"data": {"items": items}}
        )
        self.assertEqual(response.status, '200 OK')

        self.add_criteria(tender_id, owner_token)
        self.activate_tender(tender_id, owner_token)
        bid1_id, bid1_token, bid2_id, bid2_token = self.register_bids(
            tender_id, owner_token, lot_id1, lot_id2
        )

        #### Auction
        self.tick(datetime.timedelta(days=30))
        self.check_chronograph()

        self.complete_tender(tender_id, owner_token)

        with open(TARGET_DIR + 'has-auction-false-tender-complete.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_JSON_DIR + 'has-auction-false-tender-complete.json', 'w') as file_json:
            file_json.write(json.dumps(response.json, indent=4, sort_keys=True))

    def add_criteria(self, tender_id, owner_token):
        # add criteria
        test_criteria_data = deepcopy(test_exclusion_criteria)
        for i in range(len(test_criteria_data)):
            classification_id = test_criteria_data[i]['classification']['id']
            if classification_id == 'CRITERION.EXCLUSION.CONTRIBUTIONS.PAYMENT_OF_TAXES':
                del test_criteria_data[i]
                break
        test_criteria_data.extend(test_language_criteria)
        response = self.app.post_json(
            '/tenders/{}/criteria?acc_token={}'.format(tender_id, owner_token),
            {'data': test_criteria_data}
        )
        self.assertEqual(response.status, '201 Created')

    def activate_tender(self, tender_id, owner_token):
        #### Tender activating
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
            {'data': {"status": "active.tendering"}}
        )
        self.assertEqual(response.status, '200 OK')

    def register_bids(self, tender_id, owner_token, lot_id1, lot_id2):
        #### Registering bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json(
            f'/tenders/{tender_id}/bids',
            {
                'data': {
                    'selfQualified': True,
                    'status': 'draft',
                    'tenderers': test_docs_bid["tenderers"],
                    'lotValues': [{
                        "subcontractingDetails": "ДКП «Орфей», Україна",
                        "value": {"amount": 500},
                        'relatedLot': lot_id1
                    }, {
                        "subcontractingDetails": "ДКП «Орфей», Україна",
                        "value": {"amount": 500},
                        'relatedLot': lot_id2
                    }]
                }
            }
        )
        self.assertEqual(response.status, '201 Created')
        bid1_token = response.json['access']['token']
        bid1_id = response.json['data']['id']
        self.set_responses(tender_id, response.json, "active")

        #### Registering bid 2
        response = self.app.post_json(
            f'/tenders/{tender_id}/bids',
            {
                'data': {
                    'selfQualified': True,
                    'status': 'draft',
                    'tenderers': test_docs_bid2["tenderers"],
                    'lotValues': [{
                        "subcontractingDetails": "ДКП «Укр Прінт», Україна",
                        "value": {"amount": 500},
                        'relatedLot': lot_id1
                    }, {
                        "subcontractingDetails": "ДКП «Укр Прінт», Україна",
                        "value": {"amount": 500},
                        'relatedLot': lot_id2
                    }]
                }
            }
        )
        self.assertEqual(response.status, '201 Created')
        bid2_id = response.json['data']['id']
        bid2_token = response.json['access']['token']
        self.set_responses(tender_id, response.json, "active")

        return bid1_id, bid1_token, bid2_id, bid2_token

    def complete_tender(self, tender_id, owner_token):
        self.app.authorization = ('Basic', ('broker', ''))

        # Get pending award
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token))
        award = response.json["data"][0]
        award_id = award["id"]
        award2 = response.json["data"][1]
        award2_id = award2["id"]

        # Activate award
        self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_id, owner_token),
            {
                "data": {
                    "status": "active",
                    "qualified": True,
                    "eligible": True
                }
            }
        )
        self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award2_id, owner_token),
            {
                "data": {
                    "status": "active",
                    "qualified": True,
                    "eligible": True
                }
            }
        )

        #### Bypass complaintPeriod
        tender = self.mongodb.tenders.get(self.tender_id)
        for i in tender.get('awards', []):
            if "complaintPeriod" in i:
                i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.mongodb.tenders.save(tender)

        #### Activating contract
        response = self.app.get(
            '/tenders/{}/contracts?acc_token={}'.format(
                self.tender_id, owner_token
            )
        )
        self.contract_id = response.json['data'][0]['id']
        self.contract2_id = response.json['data'][1]['id']

        response = self.app.patch_json(
            '/tenders/{}/contracts/{}?acc_token={}'.format(
                self.tender_id, self.contract_id, owner_token
            ),
            {'data': {'status': 'active'}}
        )
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/contracts/{}?acc_token={}'.format(
                self.tender_id, self.contract2_id, owner_token
            ),
            {'data': {'status': 'active'}}
        )
        self.assertEqual(response.status, '200 OK')

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json["data"]["status"], 'complete')
