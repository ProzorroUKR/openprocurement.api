# -*- coding: utf-8 -*-
import datetime

import json
import csv

import os
from copy import deepcopy

import standards

from openprocurement.tender.belowthreshold.tests.utils import set_tender_lots, set_bid_lotvalues
from openprocurement.tender.open.tests.tender import BaseTenderUAWebTest
from openprocurement.tender.core.tests.base import (
    test_exclusion_criteria,
    test_language_criteria,
)
from openprocurement.contracting.econtract.tests.data import test_signer_info
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
    test_docs_tender_below,
    test_docs_question,
    test_docs_items_open,
    test_docs_claim,
    test_docs_tender_dps,
)

TARGET_DIR = 'docs/source/tendering/config/http/'
TARGET_JSON_DIR = 'docs/source/tendering/config/json/'
TARGET_CSV_DIR = 'docs/source/tendering/config/csv/'


class TenderConfigCSVMixin:
    def write_config_values_csv(self, config_name, file_path):
        pmts = [
            "aboveThreshold",
            "competitiveOrdering",
            "aboveThresholdEU",
            "aboveThresholdUA.defense",
            "aboveThresholdUA",
            "belowThreshold",
            "closeFrameworkAgreementSelectionUA",
            "closeFrameworkAgreementUA",
            "competitiveDialogueEU",
            "competitiveDialogueEU.stage2",
            "competitiveDialogueUA",
            "competitiveDialogueUA.stage2",
            "esco",
            "negotiation",
            "negotiation.quick",
            "priceQuotation",
            "reporting",
            "simple.defense",
        ]

        headers = [
            "procurementMethodType",
            "values",
            "default",
        ]

        rows = []

        for pmt in pmts:
            schema = standards.load(f"data_model/schema/TenderConfig/{pmt}.json")
            config_schema = schema["properties"][config_name]
            row = self.get_config_row(pmt, config_schema)
            rows.append(row)

        with open(file_path, "w") as file_csv:
            writer = csv.writer(file_csv)
            writer.writerow(headers)
            writer.writerows(rows)
    def write_config_pmt_csv(self, pmt, file_path):
        headers = [
            "name",
            "values",
            "default",
        ]

        rows = []

        schema = standards.load(f"data_model/schema/TenderConfig/{pmt}.json")

        for config_name, config_schema in schema["properties"].items():
            row = self.get_config_row(config_name, config_schema)
            rows.append(row)

        with open(file_path, "w") as file_csv:
            writer = csv.writer(file_csv)
            writer.writerow(headers)
            writer.writerows(rows)

    def get_config_row(self, name, config_schema):
        row = []

        # row name
        row.append(name)

        # possible values
        row.append(self.get_config_possible_values(config_schema))

        # default value
        config_default = config_schema.get("default", "")
        row.append(json.dumps(config_default))

        return row

    def get_config_possible_values(self, config_schema):
        separator = ","
        empty = ""
        if "enum" in config_schema:
            config_values_enum = config_schema.get("enum", "")
            config_values = separator.join(map(json.dumps, config_values_enum))
            return config_values
        elif "minimum" in config_schema and "maximum" in config_schema:
            config_values_min = config_schema.get("minimum", "")
            config_values_max = config_schema.get("maximum", "")
            if config_values_min == config_values_max:
                return config_values_min
            else:
                return f'{config_values_min} - {config_values_max}'
        else:
            return empty

class TenderConfigBaseResourceTest(BaseTenderUAWebTest, MockWebTestMixin, TenderConfigCSVMixin):
    AppClass = DumpsWebTestApp

    relative_to = os.path.dirname(__file__)
    initial_data = test_docs_tender_open
    docservice = True
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL

    whitelist = ('/openprocurement/.*models.*', )
    blacklist = ('/tests/.*\.py',)

    def setUp(self):
        super(TenderConfigBaseResourceTest, self).setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super(TenderConfigBaseResourceTest, self).tearDown()

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

    def activating_contract(self, contract_id, owner_token, bid_token):
        response = self.app.put_json(
            f'/contracts/{contract_id}/buyer/signer_info?acc_token={owner_token}',
            {"data": test_signer_info}
        )
        self.assertEqual(response.status, '200 OK')

        response = self.app.put_json(
            f'/contracts/{contract_id}/suppliers/signer_info?acc_token={bid_token}',
            {"data": test_signer_info}
        )

        self.assertEqual(response.status, '200 OK')
        response = self.app.patch_json(
            f'/contracts/{contract_id}?acc_token={owner_token}',
            {'data': {'status': 'active'}}
        )
        self.assertEqual(response.status, '200 OK')


class TenderHasAuctionResourceTest(TenderConfigBaseResourceTest):

    def test_docs_has_auction_values_csv(self):
        self.write_config_values_csv(
            config_name="hasAuction",
            file_path=TARGET_CSV_DIR + "has-auction-values.csv",
        )

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

        self.app.authorization = ('Basic', ('broker', ''))

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


        self.complete_tender(tender_id, owner_token, bid1_token)

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

        self.bid_token = bid1_token

        #### Auction
        self.tick(datetime.timedelta(days=30))
        self.check_chronograph()

        self.complete_tender(tender_id, owner_token, bid1_token)

        with open(TARGET_DIR + 'has-auction-false-tender-complete.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_JSON_DIR + 'has-auction-false-tender-complete.json', 'w') as file_json:
            file_json.write(json.dumps(response.json, indent=4, sort_keys=True))

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
        self.set_responses(tender_id, response.json, "pending")

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
        self.set_responses(tender_id, response.json, "pending")

        return bid1_id, bid1_token, bid2_id, bid2_token

    def complete_tender(self, tender_id, owner_token, bid_token):
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

        for contract in response.json["data"]:
            self.activating_contract(contract["id"], owner_token, bid_token)

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json["data"]["status"], 'complete')


class TenderHasAwardingResourceTest(TenderConfigBaseResourceTest):

    def test_docs_has_value_restriction_values_csv(self):
        self.write_config_values_csv(
            config_name="hasAwardingOrder",
            file_path=TARGET_CSV_DIR + "has-awarding-order-values.csv",
        )

    def register_bids(self, tender_id, lot_id1, lot_id2):
        self.app.authorization = ('Basic', ('broker', ''))
        bid_data = {
            'status': 'draft',
            'tenderers': test_docs_bid["tenderers"],
            'lotValues': [{
                "value": {"amount": 300},
                'relatedLot': lot_id1
            }, {
                "value": {"amount": 500},
                'relatedLot': lot_id2
            }]
        }
        response = self.app.post_json(
            '/tenders/{}/bids'.format(self.tender_id),
            {'data': bid_data}
        )
        self.assertEqual(response.status, '201 Created')
        bid1_id = response.json['data']['id']
        bid1_token = response.json['access']['token']
        self.set_responses(tender_id, response.json, "pending")

        bid_data["lotValues"][0]["value"]["amount"] = 500
        bid_data["lotValues"][1]["value"]["amount"] = 400
        response = self.app.post_json(
            '/tenders/{}/bids'.format(self.tender_id),
            {'data': bid_data}
        )
        self.assertEqual(response.status, '201 Created')
        bid2_id = response.json['data']['id']
        bid2_token = response.json['access']['token']
        self.set_responses(tender_id, response.json, "pending")

        return bid1_id, bid1_token, bid2_id, bid2_token

    def test_docs_has_awarding_order_true(self):
        config = deepcopy(self.initial_config)
        config["hasAwardingOrder"] = True

        test_tender_data = deepcopy(test_docs_tender_below)
        test_tender_data["awardCriteria"] = "lowestCost"
        test_tender_data["items"] = test_docs_items_open
        test_lots = deepcopy(test_docs_lots)
        test_lots[0]['value'] = test_tender_data['value']
        test_lots[0]['minimalStep'] = test_tender_data['minimalStep']
        test_lots[1]['value'] = test_tender_data['value']
        test_lots[1]['minimalStep'] = test_tender_data['minimalStep']

        # Creating tender

        with open(TARGET_DIR + 'has-awarding-order-true-tender-post.http', 'w') as self.app.file_obj:
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
        with open(TARGET_DIR + 'has-awarding-order-true-tender-add-lot.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                {'data': test_lots[0]}
            )
            self.assertEqual(response.status, '201 Created')
            lot_id1 = response.json['data']['id']
        response = self.app.post_json(
            '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
            {'data': test_lots[0]}
        )
        self.assertEqual(response.status, '201 Created')
        lot_id2 = response.json['data']['id']

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
        # Tender activating

        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
            {'data': {"status": "active.enquiries"}}
        )
        self.assertEqual(response.status, '200 OK')

        # enquires
        response = self.app.post_json(
            '/tenders/{}/questions'.format(tender_id),
            {"data": test_docs_question}, status=201
        )
        question_id = response.json['data']['id']
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json(
            '/tenders/{}/questions/{}?acc_token={}'.format(
                tender_id, question_id, owner_token
            ),
            {
                "data": {
                    "answer": "Таблицю додано в файлі \"Kalorijnist.xslx\""
                }
            }, status=200
        )
        self.assertEqual(response.status, '200 OK')
        self.set_status('active.tendering')
        bid1_id, bid1_token, bid2_id, bid2_token = self.register_bids(
            tender_id, lot_id1, lot_id2
        )

        #### Auction
        self.set_status('active.auction')

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
        self.app.post_json(
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

        with open(TARGET_DIR + 'has-awarding-order-true-auction-results.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_JSON_DIR + 'has-awarding-order-true-auction-results.json', 'w') as file_json:
            file_json.write(json.dumps(response.json, indent=4, sort_keys=True))

    def test_docs_has_awarding_order_false(self):
        config = deepcopy(self.initial_config)
        config["hasAwardingOrder"] = False

        test_tender_data = deepcopy(test_docs_tender_below)
        test_tender_data["items"] = test_docs_items_open
        test_lots = deepcopy(test_docs_lots)
        test_lots[0]['value'] = test_tender_data['value']
        test_lots[0]['minimalStep'] = test_tender_data['minimalStep']
        test_lots[1]['value'] = test_tender_data['value']
        test_lots[1]['minimalStep'] = test_tender_data['minimalStep']

        # Creating tender

        with open(TARGET_DIR + 'has-awarding-order-false-tender-post.http', 'w') as self.app.file_obj:
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
        with open(TARGET_DIR + 'has-awarding-order-false-tender-add-lot.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                {'data': test_lots[0]}
            )
            self.assertEqual(response.status, '201 Created')
            lot_id1 = response.json['data']['id']
        response = self.app.post_json(
            '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
            {'data': test_lots[0]}
        )
        self.assertEqual(response.status, '201 Created')
        lot_id2 = response.json['data']['id']

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
        # Tender activating

        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
            {'data': {"status": "active.enquiries"}}
        )
        self.assertEqual(response.status, '200 OK')

        # enquires
        response = self.app.post_json(
            '/tenders/{}/questions'.format(tender_id),
            {"data": test_docs_question}, status=201
        )
        question_id = response.json['data']['id']
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json(
            '/tenders/{}/questions/{}?acc_token={}'.format(
                tender_id, question_id, owner_token
            ),
            {
                "data": {
                    "answer": "Таблицю додано в файлі \"Kalorijnist.xslx\""
                }
            }, status=200
        )
        self.assertEqual(response.status, '200 OK')
        self.set_status('active.tendering')
        bid1_id, bid1_token, bid2_id, bid2_token = self.register_bids(
            tender_id, lot_id1, lot_id2
        )

        #### Auction
        self.set_status('active.auction')

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
        self.app.post_json(
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
        self.app.post_json(
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

        with open(TARGET_DIR + 'has-awarding-order-false-auction-results.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_JSON_DIR + 'has-awarding-order-false-auction-results.json', 'w') as file_json:
            file_json.write(json.dumps(response.json, indent=4, sort_keys=True))

    def test_docs_has_awarding_order_false_with_3_bidders(self):
        config = deepcopy(self.initial_config)
        config["hasAwardingOrder"] = False

        test_tender_data = deepcopy(test_docs_tender_below)
        test_lots = deepcopy(test_docs_lots[:1])
        test_lots[0]['value'] = test_tender_data['value']
        test_lots[0]['minimalStep'] = test_tender_data['minimalStep']
        set_tender_lots(test_tender_data, test_lots)

        # Creating tender
        response = self.app.post_json(
            '/tenders?opt_pretty=1',
            {'data': test_tender_data, 'config': config}
        )
        self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']
        lots = response.json['data']["lots"]
        lot_id = lots[0]["id"]

        self.app.authorization = ('Basic', ('broker', ''))
        self.add_criteria(tender_id, owner_token)

        # Tender activating
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
            {'data': {"status": "active.enquiries"}}
        )
        self.assertEqual(response.status, '200 OK')

        # enquires
        response = self.app.post_json(
            '/tenders/{}/questions'.format(tender_id),
            {"data": test_docs_question}, status=201
        )
        question_id = response.json['data']['id']
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json(
            '/tenders/{}/questions/{}?acc_token={}'.format(
                tender_id, question_id, owner_token
            ),
            {
                "data": {
                    "answer": "Таблицю додано в файлі \"Kalorijnist.xslx\""
                }
            }, status=200
        )
        self.assertEqual(response.status, '200 OK')
        self.set_status('active.tendering')

        # register bids
        bids = []
        bids_tokens = []
        for idx in range(3):
            self.app.authorization = ('Basic', ('broker', ''))
            bid_data = {
                'status': 'draft',
                'tenderers': test_docs_bid["tenderers"],
                "value": {
                    "amount": 500 - idx
                }
            }
            set_bid_lotvalues(bid_data, lots)
            response = self.app.post_json(
                '/tenders/{}/bids'.format(self.tender_id),
                {'data': bid_data}
            )
            self.assertEqual(response.status, '201 Created')
            bids.append(response.json['data']['id'])
            bids_tokens.append(response.json['access']['token'])
            self.set_responses(tender_id, response.json, "pending")

        #### Auction
        self.set_status('active.auction')

        self.app.authorization = ('Basic', ('auction', ''))
        auction_url = '{}/tenders/{}_{}'.format(self.auctions_url, self.tender_id, lot_id)
        patch_data = {
            'lots': [
                {
                    'id': lot_id,
                    'auctionUrl': auction_url,
                },
            ],
            'bids': [{
                "id": bids[0],
                "lotValues": [
                    {"participationUrl": '{}?key_for_bid={}'.format(auction_url, bids[0])}
                ]
            }, {
                "id": bids[1],
                "lotValues": [
                    {"participationUrl": '{}?key_for_bid={}'.format(auction_url, bids[1])},
                ]
            }, {
                "id": bids[2],
                "lotValues": [
                    {"participationUrl": '{}?key_for_bid={}'.format(auction_url, bids[2])},
                ]
            }]
        }
        response = self.app.patch_json(
            '/tenders/{}/auction/{}?acc_token={}'.format(self.tender_id, lot_id, owner_token),
            {'data': patch_data}
        )
        self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))

        #### Confirming qualification
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        self.app.post_json(
            '/tenders/{}/auction/{}'.format(self.tender_id, lot_id),
            {
                'data': {
                    'bids': [
                        {
                            "id": b["id"],
                            "lotValues": [
                                {"value": lot["value"], "relatedLot": lot["relatedLot"]}
                                for lot in b["lotValues"]
                            ]
                        }
                        for b in auction_bids_data
                    ]
                }
            }
        )
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        award_1_id = response.json["data"]["awards"][0]["id"]
        award_2_id = response.json["data"]["awards"][1]["id"]

        with open(TARGET_DIR + 'has-awarding-order-false-auction-results-example-1.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')

        self.app.authorization = ('Basic', ('broker', ''))
        # The customer decides that the winner is award1
        with open(TARGET_DIR + 'has-awarding-order-false-auction-results-example-1-activate-first-award.http',
                  'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_1_id, owner_token),
                {'data': {'status': 'active'}}
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'has-awarding-order-false-auction-results-example-1-results.http',
                  'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token),
            )
            self.assertEqual(response.status, '200 OK')

        # The customer cancels decision due to award1
        with open(TARGET_DIR + 'has-awarding-order-false-auction-results-example-2-cancel-first-award.http',
                  'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_1_id, owner_token),
                {'data': {'status': 'cancelled'}}
            )
            self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'has-awarding-order-false-auction-results-example-2-results.http',
                  'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token),
            )
            self.assertEqual(response.status, '200 OK')
            award_4_id = response.json["data"][-1]["id"]

        # The customer rejects award4 (1.1) and recognizes as the winner award2
        response = self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_4_id, owner_token),
            {'data': {'status': 'unsuccessful'}}
        )
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_2_id, owner_token),
            {'data': {'status': 'active'}}
        )
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'has-awarding-order-false-auction-results-example-3-results.http',
                  'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token),
            )
            self.assertEqual(response.status, '200 OK')

        claim = deepcopy(test_docs_claim)
        claim_data = {'data': claim}
        claim_data['data']['status'] = 'claim'
        response = self.app.post_json(
            '/tenders/{}/awards/{}/complaints?acc_token={}'.format(
                self.tender_id, award_4_id, bids_tokens[0]), claim_data)
        self.assertEqual(response.status, '201 Created')

        complaint_token = response.json['access']['token']
        complaint_id = response.json['data']['id']

        response = self.app.patch_json(
            '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                self.tender_id, award_4_id, complaint_id, owner_token),
            {'data': {
                "status": "answered",
                "resolutionType": "resolved",
                "resolution": "Умови виправлено, вибір переможня буде розгянуто повторно"
            }})
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                self.tender_id, award_4_id, complaint_id, complaint_token),
            {'data': {
                "satisfied": True,
            }})
        self.assertEqual(response.status, '200 OK')

        # The customer cancel unsuccessful award4
        self.assertEqual(response.status, '200 OK')
        response = self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_4_id, owner_token),
            {'data': {'status': 'cancelled'}}
        )
        self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'has-awarding-order-false-auction-results-example-4-results.http',
                  'w') as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token),
            )
            self.assertEqual(response.status, '200 OK')


class TenderHasValueRestrictionResourceTest(TenderConfigBaseResourceTest):

    def test_docs_has_value_restriction_values_csv(self):
        self.write_config_values_csv(
            config_name="hasValueRestriction",
            file_path=TARGET_CSV_DIR + "has-value-restriction-values.csv",
        )

    def test_docs_lots_has_value_restriction_true(self):
        config = deepcopy(self.initial_config)
        config["hasValueRestriction"] = True

        test_tender_data = deepcopy(test_docs_tender_below)
        test_tender_data["items"] = test_docs_items_open
        test_lots = deepcopy(test_docs_lots)
        test_lots[0]['value'] = test_tender_data['value']
        test_lots[0]['minimalStep'] = test_tender_data['minimalStep']
        test_lots[1]['value'] = test_tender_data['value']
        test_lots[1]['minimalStep'] = test_tender_data['minimalStep']

        #### Creating tender

        with open(TARGET_DIR + 'has-value-restriction-true-tender-lots-post.http', 'w') as self.app.file_obj:
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

        # Tender activating
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
            {'data': {"status": "active.enquiries"}}
        )
        self.assertEqual(response.status, '200 OK')

        # enquires
        response = self.app.post_json(
            '/tenders/{}/questions'.format(tender_id),
            {"data": test_docs_question}, status=201
        )
        question_id = response.json['data']['id']
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json(
            '/tenders/{}/questions/{}?acc_token={}'.format(
                tender_id, question_id, owner_token
            ),
            {
                "data": {
                    "answer": "Таблицю додано в файлі \"Kalorijnist.xslx\""
                }
            }, status=200
        )
        self.assertEqual(response.status, '200 OK')
        self.set_status('active.tendering')

        #### Registering bid
        with open(TARGET_DIR + 'has-value-restriction-true-tender-lots-add-invalid-bid.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f'/tenders/{tender_id}/bids',
                {
                    'data': {
                        'status': 'draft',
                        'tenderers': test_docs_bid["tenderers"],
                        'lotValues': [{
                            "value": {"amount": 600},
                            'relatedLot': lot_id1
                        }, {
                            "value": {"amount": 500},
                            'relatedLot': lot_id2
                        }]
                    }
                },
                status=422,
            )
            self.assertEqual(response.status, "422 Unprocessable Entity")
            self.assertEqual(
                response.json["errors"],
                [{
                    "location": "body",
                    "name": "lotValues",
                    "description": [{"value": ["value of bid should be less than value of lot"]}]
                }]
            )

        with open(TARGET_DIR + 'has-value-restriction-true-tender-lots-add-valid-bid.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f'/tenders/{tender_id}/bids',
                {
                    'data': {
                        'status': 'draft',
                        'tenderers': test_docs_bid["tenderers"],
                        'lotValues': [{
                            "value": {"amount": 500},
                            'relatedLot': lot_id1
                        }, {
                            "value": {"amount": 500},
                            'relatedLot': lot_id2
                        }]
                    }
                }
            )
            self.assertEqual(response.status, "201 Created")
            bid_token = response.json['access']['token']
            bid_id = response.json['data']['id']

        with open(TARGET_DIR + 'has-value-restriction-true-tender-lots-patch-bid.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/tenders/{tender_id}/bids/{bid_id}?acc_token={bid_token}',
                {
                    'data': {
                        'status': 'active',
                        'tenderers': test_docs_bid["tenderers"],
                        'lotValues': [{
                            "value": {"amount": 500},
                            'relatedLot': lot_id1
                        }, {
                            "value": {"amount": 700},
                            'relatedLot': lot_id2
                        }]
                    }
                },
                status=422,
            )
            self.assertEqual(response.status, "422 Unprocessable Entity")
            self.assertEqual(
                response.json["errors"],
                [{
                    "location": "body",
                    "name": "lotValues",
                    "description": [{"value": ["value of bid should be less than value of lot"]}]
                }]
            )

    def test_docs_lots_has_value_restriction_false(self):
        config = deepcopy(self.initial_config)
        config["hasValueRestriction"] = False

        test_tender_data = deepcopy(test_docs_tender_below)
        test_tender_data["items"] = test_docs_items_open
        test_lots = deepcopy(test_docs_lots)
        test_lots[0]['value'] = test_tender_data['value']
        test_lots[0]['minimalStep'] = test_tender_data['minimalStep']
        test_lots[1]['value'] = test_tender_data['value']
        test_lots[1]['minimalStep'] = test_tender_data['minimalStep']

        #### Creating tender

        with open(TARGET_DIR + 'has-value-restriction-false-tender-lots-post.http', 'w') as self.app.file_obj:
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

        # Tender activating
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
            {'data': {"status": "active.enquiries"}}
        )
        self.assertEqual(response.status, '200 OK')

        # enquires
        response = self.app.post_json(
            '/tenders/{}/questions'.format(tender_id),
            {"data": test_docs_question}, status=201
        )
        question_id = response.json['data']['id']
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json(
            '/tenders/{}/questions/{}?acc_token={}'.format(
                tender_id, question_id, owner_token
            ),
            {
                "data": {
                    "answer": "Таблицю додано в файлі \"Kalorijnist.xslx\""
                }
            }, status=200
        )
        self.assertEqual(response.status, '200 OK')
        self.set_status('active.tendering')

        #### Registering bid
        with open(TARGET_DIR + 'has-value-restriction-false-tender-lots-add-valid-bid.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f'/tenders/{tender_id}/bids',
                {
                    'data': {
                        'status': 'draft',
                        'tenderers': test_docs_bid["tenderers"],
                        'lotValues': [{
                            "value": {"amount": 600},
                            'relatedLot': lot_id1
                        }, {
                            "value": {"amount": 700},
                            'relatedLot': lot_id2
                        }]
                    }
                },
            )
            self.assertEqual(response.status, "201 Created")


class TenderValueCurrencyEqualityResourceTest(TenderConfigBaseResourceTest):

    def test_docs_value_currency_equality_values_csv(self):
        self.write_config_values_csv(
            config_name="valueCurrencyEquality",
            file_path=TARGET_CSV_DIR + "value-currency-equality-values.csv",
        )

    def test_docs_lots_value_currency_equality_true(self):
        config = deepcopy(self.initial_config)
        config["valueCurrencyEquality"] = True

        test_tender_data = deepcopy(test_docs_tender_below)
        test_tender_data["items"] = test_docs_items_open
        test_lots = deepcopy(test_docs_lots)
        test_lots[0]['value'] = test_tender_data['value']
        test_lots[0]['minimalStep'] = test_tender_data['minimalStep']
        test_lots[1]['value'] = test_tender_data['value']
        test_lots[1]['minimalStep'] = test_tender_data['minimalStep']

        # Creating tender

        with open(TARGET_DIR + 'value-currency-equality-true-tender-lots-post.http', 'w') as self.app.file_obj:
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

        # Tender activating
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
            {'data': {"status": "active.enquiries"}}
        )
        self.assertEqual(response.status, '200 OK')

        # enquires
        response = self.app.post_json(
            '/tenders/{}/questions'.format(tender_id),
            {"data": test_docs_question}, status=201
        )
        question_id = response.json['data']['id']
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json(
            '/tenders/{}/questions/{}?acc_token={}'.format(
                tender_id, question_id, owner_token
            ),
            {
                "data": {
                    "answer": "Таблицю додано в файлі \"Kalorijnist.xslx\""
                }
            }, status=200
        )
        self.assertEqual(response.status, '200 OK')
        self.set_status('active.tendering')

        # Registering bid

        with open(TARGET_DIR + 'value-currency-equality-true-tender-lots-add-invalid-bid.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f'/tenders/{tender_id}/bids',
                {
                    'data': {
                        'status': 'draft',
                        'tenderers': test_docs_bid["tenderers"],
                        'lotValues': [{
                            "value": {"amount": 600, "currency": "USD"},
                            'relatedLot': lot_id1
                        }, {
                            "value": {"amount": 500, "currency": "UAH"},
                            'relatedLot': lot_id2
                        }]
                    }
                },
                status=422,
            )
            self.assertEqual(response.status, "422 Unprocessable Entity")
            self.assertEqual(
                response.json["errors"],
                [{
                    "location": "body",
                    "name": "lotValues",
                    "description": [{"value": ["currency of bid should be identical to currency of value of lot"]}]
                }]
            )

        with open(TARGET_DIR + 'value-currency-equality-true-tender-lots-add-valid-bid.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f'/tenders/{tender_id}/bids',
                {
                    'data': {
                        'status': 'draft',
                        'tenderers': test_docs_bid["tenderers"],
                        'lotValues': [{
                            "value": {"amount": 500, "currency": "UAH"},
                            'relatedLot': lot_id1
                        }, {
                            "value": {"amount": 500, "currency": "UAH"},
                            'relatedLot': lot_id2
                        }]
                    }
                }
            )
            self.assertEqual(response.status, "201 Created")
            bid_token = response.json['access']['token']
            bid_id = response.json['data']['id']

        with open(TARGET_DIR + 'value-currency-equality-true-tender-lots-patch-bid.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                f'/tenders/{tender_id}/bids/{bid_id}?acc_token={bid_token}',
                {
                    'data': {
                        'status': 'active',
                        'tenderers': test_docs_bid["tenderers"],
                        'lotValues': [{
                            "value": {"amount": 500, "currency": "UAH"},
                            'relatedLot': lot_id1
                        }, {
                            "value": {"amount": 700, "currency": "USD"},
                            'relatedLot': lot_id2
                        }]
                    }
                },
                status=422,
            )
            self.assertEqual(response.status, "422 Unprocessable Entity")
            self.assertEqual(
                response.json["errors"],
                [{
                    "location": "body",
                    "name": "lotValues",
                    "description": [{"value": ["currency of bid should be identical to currency of value of lot"]}]
                }]
            )

    def test_docs_lots_value_currency_equality_false(self):
        config = deepcopy(self.initial_config)
        config.update({
            "valueCurrencyEquality": False,
            "hasAuction": False,
            "hasAwardingOrder": False,
            "hasValueRestriction": False,
        })

        test_tender_data = deepcopy(test_docs_tender_below)
        test_tender_data["items"] = test_docs_items_open
        del test_tender_data["minimalStep"]
        test_lots = deepcopy(test_docs_lots)
        test_lots[0]['value'] = test_tender_data['value']
        test_lots[1]['value'] = test_tender_data['value']

        # Creating tender

        with open(TARGET_DIR + 'value-currency-equality-false-tender-lots-post.http', 'w') as self.app.file_obj:
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

        # Tender activating
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
            {'data': {"status": "active.enquiries"}}
        )
        self.assertEqual(response.status, '200 OK')

        # enquires
        response = self.app.post_json(
            '/tenders/{}/questions'.format(tender_id),
            {"data": test_docs_question}, status=201
        )
        question_id = response.json['data']['id']
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json(
            '/tenders/{}/questions/{}?acc_token={}'.format(
                tender_id, question_id, owner_token
            ),
            {
                "data": {
                    "answer": "Таблицю додано в файлі \"Kalorijnist.xslx\""
                }
            }, status=200
        )
        self.assertEqual(response.status, '200 OK')
        self.set_status('active.tendering')

        # Registering bid
        with open(TARGET_DIR + 'value-currency-equality-false-tender-lots-add-valid-bid.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f'/tenders/{tender_id}/bids',
                {
                    'data': {
                        'status': 'draft',
                        'tenderers': test_docs_bid["tenderers"],
                        'lotValues': [{
                            "value": {"amount": 600, "currency": "USD"},
                            'relatedLot': lot_id1
                        }, {
                            "value": {"amount": 700, "currency": "EUR"},
                            'relatedLot': lot_id2
                        }]
                    }
                },
            )
            self.assertEqual(response.status, "201 Created")
            self.set_responses(tender_id, response.json, "pending")
        bid_token = response.json["access"]["token"]

        # Auction
        self.tick(datetime.timedelta(days=30))
        self.check_chronograph()

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
                }
            }
        )
        self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award2_id, owner_token),
            {
                "data": {
                    "status": "active",
                    "qualified": True,
                }
            }
        )

        # Bypass complaintPeriod
        tender = self.mongodb.tenders.get(self.tender_id)
        for i in tender.get('awards', []):
            if "complaintPeriod" in i:
                i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.mongodb.tenders.save(tender)

        # Activating contract
        response = self.app.get(
            '/tenders/{}/contracts?acc_token={}'.format(
                self.tender_id, owner_token
            )
        )
        self.contract_id = response.json['data'][0]['id']
        self.contract2_id = response.json['data'][1]['id']

        for contract_id in (self.contract_id, self.contract2_id):
            self.activating_contract(contract_id, owner_token, bid_token)

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json["data"]["status"], 'complete')

        with open(TARGET_DIR + 'value-currency-equality-false-tender-complete.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')


class TenderMinBidsNumberResourceTest(TenderConfigBaseResourceTest):
    initial_data = deepcopy(test_docs_tender_below)

    def test_docs_min_bids_number_values_csv(self):
        self.write_config_values_csv(
            config_name="minBidsNumber",
            file_path=TARGET_CSV_DIR + "min-bids-number-values.csv",
        )

    def activate_tender(self, tender_id, owner_token):
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
            {'data': {"status": "active.enquiries"}}
        )
        self.assertEqual(response.status, '200 OK')

        # enquires
        response = self.app.post_json(
            '/tenders/{}/questions'.format(tender_id),
            {"data": test_docs_question}, status=201
        )
        question_id = response.json['data']['id']
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json(
            '/tenders/{}/questions/{}?acc_token={}'.format(
                tender_id, question_id, owner_token
            ),
            {
                "data": {
                    "answer": "Таблицю додано в файлі \"Kalorijnist.xslx\""
                }
            }, status=200
        )
        self.assertEqual(response.status, '200 OK')
        self.set_status('active.tendering')

    def register_bid(self, tender_id, lot_ids, initial_amount=300):
        bid_data = {
            'status': 'draft',
            'tenderers': test_docs_bid["tenderers"],
            'lotValues': []
        }
        for idx, lot_id in enumerate(lot_ids):
            bid_data["lotValues"].append({
                "value": {"amount": idx * 100 + initial_amount},
                'relatedLot': lot_id
            })
        response = self.app.post_json(
            '/tenders/{}/bids'.format(self.tender_id),
            {'data': bid_data}
        )
        self.assertEqual(response.status, '201 Created')
        self.set_responses(tender_id, response.json, "pending")
        return response.json['data']['id']

    def test_docs_min_bids_number_invalid_config(self):
        config = deepcopy(self.initial_config)
        config["minBidsNumber"] = 0
        config["hasValueRestriction"] = True

        with open(TARGET_DIR + 'min-bids-number-invalid-value-1.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': self.initial_data, 'config': config},
                status=422,
            )
            self.assertEqual(response.status, "422 Unprocessable Entity")
            self.assertEqual(
                response.json["errors"],
                [{
                    "location": "body",
                    "name": "minBidsNumber",
                    "description": "0 is less than the minimum of 1"
                }]
            )

        config["minBidsNumber"] = 10
        with open(TARGET_DIR + 'min-bids-number-invalid-value-2.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': self.initial_data, 'config': config},
                status=422,
            )
            self.assertEqual(response.status, "422 Unprocessable Entity")
            self.assertEqual(
                response.json["errors"],
                [{
                    "location": "body",
                    "name": "minBidsNumber",
                    "description": "10 is greater than the maximum of 9"
                }]
            )

    def test_docs_min_bids_number_tendering_unsuccessful(self):
        config = deepcopy(self.initial_config)
        config["minBidsNumber"] = 2
        config["hasValueRestriction"] = True

        with open(TARGET_DIR + 'min-bids-number-tender-post-1.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': self.initial_data, 'config': config},
            )
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        self.app.authorization = ('Basic', ('broker', ''))

        # add lot
        test_lot = deepcopy(test_docs_lots[0])
        test_lot['value'] = self.initial_data['value']
        test_lot['minimalStep'] = self.initial_data['minimalStep']
        response = self.app.post_json(
            '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
            {'data': test_lot}
        )
        self.assertEqual(response.status, '201 Created')
        lot = response.json['data']
        lot_id = lot['id']

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = lot_id
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
            {"data": {"items": items}}
        )
        self.assertEqual(response.status, '200 OK')

        self.add_criteria(tender_id, owner_token)
        self.activate_tender(tender_id, owner_token)

        self.register_bid(tender_id, [lot_id])

        self.tick(datetime.timedelta(days=30))
        self.check_chronograph()
        with open(TARGET_DIR + 'min-bids-number-tender-unsuccessful.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'unsuccessful')

    def test_docs_min_bids_number_tendering_one_bid(self):
        config = deepcopy(self.initial_config)
        config["minBidsNumber"] = 1
        config["hasValueRestriction"] = True

        with open(TARGET_DIR + 'min-bids-number-tender-post-2.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': self.initial_data, 'config': config},
            )
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        self.app.authorization = ('Basic', ('broker', ''))

        # add lot
        test_lot = deepcopy(test_docs_lots[0])
        test_lot['value'] = self.initial_data['value']
        test_lot['minimalStep'] = self.initial_data['minimalStep']
        response = self.app.post_json(
            '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
            {'data': test_lot}
        )
        self.assertEqual(response.status, '201 Created')
        lot = response.json['data']
        lot_id = lot['id']

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = lot_id
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
            {"data": {"items": items}}
        )
        self.assertEqual(response.status, '200 OK')

        self.add_criteria(tender_id, owner_token)
        self.activate_tender(tender_id, owner_token)

        self.register_bid(tender_id, [lot_id])

        self.tick(datetime.timedelta(days=30))
        self.check_chronograph()
        with open(TARGET_DIR + 'min-bids-number-tender-qualification-1.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active.qualification')

    def test_docs_min_bids_number_tendering_two_bids_qualification(self):
        config = deepcopy(self.initial_config)
        config["minBidsNumber"] = 2

        test_tender_data = deepcopy(test_docs_tender_below)
        test_tender_data['items'] = test_docs_items_open
        test_lots = deepcopy(test_docs_lots)
        test_lots[0]['value'] = test_tender_data['value']
        test_lots[0]['minimalStep'] = test_tender_data['minimalStep']
        test_lots[1]['value'] = test_tender_data['value']
        test_lots[1]['minimalStep'] = test_tender_data['minimalStep']

        with open(TARGET_DIR + 'min-bids-number-tender-post-3.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': test_tender_data, 'config': config},
            )
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        self.app.authorization = ('Basic', ('broker', ''))

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

        bid1_id = self.register_bid(tender_id, [lot_id1, lot_id2])
        bid2_id = self.register_bid(tender_id, [lot_id1, lot_id2], initial_amount=400)

        # Auction
        self.set_status('active.auction')
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

        # Confirming qualification
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        self.app.post_json(
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
        self.app.post_json(
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

        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'min-bids-number-tender-qualification-2.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active.qualification')


class TenderHasPrequalificationResourceTest(TenderConfigBaseResourceTest):

    def test_docs_has_prequalification_values_csv(self):
        self.write_config_values_csv(
            config_name="hasPrequalification",
            file_path=TARGET_CSV_DIR + "has-prequalification-values.csv",
        )


class TenderHasPreSelectionAgreementResourceTest(TenderConfigBaseResourceTest):

    def test_docs_has_pre_selection_agreement_values_csv(self):
        self.write_config_values_csv(
            config_name="hasPreSelectionAgreement",
            file_path=TARGET_CSV_DIR + "has-pre-selection-agreement-values.csv",
        )