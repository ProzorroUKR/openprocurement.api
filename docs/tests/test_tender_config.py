import csv
import datetime
import json
import os
from copy import deepcopy
from hashlib import sha512
from uuid import uuid4

import standards
from dateutil.parser import parse
from tests.base.constants import AUCTIONS_URL, DOCS_URL, MOCK_DATETIME
from tests.base.data import (
    test_docs_bid,
    test_docs_bid2,
    test_docs_bid3_with_docs,
    test_docs_bid_document,
    test_docs_bid_document2,
    test_docs_bid_draft,
    test_docs_claim,
    test_docs_items_open,
    test_docs_lots,
    test_docs_qualified,
    test_docs_question,
    test_docs_subcontracting,
    test_docs_tender_below,
    test_docs_tender_below_maximum,
    test_docs_tender_dps,
    test_docs_tender_esco,
    test_docs_tender_open,
)
from tests.base.test import DumpsWebTestApp, MockWebTestMixin

from openprocurement.api.context import get_now, set_now
from openprocurement.api.mask import MASK_STRING
from openprocurement.api.tests.base import change_auth
from openprocurement.contracting.api.tests.data import test_contract_data
from openprocurement.contracting.core.procedure.mask import CONTRACT_MASK_MAPPING
from openprocurement.contracting.econtract.tests.data import test_signer_info
from openprocurement.framework.dps.tests.base import (
    test_framework_dps_config,
    test_framework_dps_data,
    test_submission_config,
    test_submission_data,
)
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_config
from openprocurement.tender.belowthreshold.tests.utils import (
    set_bid_lotvalues,
    set_tender_lots,
)
from openprocurement.tender.core.procedure.mask import TENDER_MASK_MAPPING
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.core.tests.base import (
    test_contract_guarantee_criteria,
    test_exclusion_criteria,
    test_language_criteria,
)
from openprocurement.tender.core.utils import calculate_clarif_business_date
from openprocurement.tender.esco.tests.base import test_tender_esco_config
from openprocurement.tender.open.tests.base import (
    test_tender_dps_config,
    test_tender_open_config,
)
from openprocurement.tender.open.tests.tender import BaseTenderUAWebTest
from openprocurement.tender.openeu.tests.base import test_tender_openeu_config
from openprocurement.tender.openeu.tests.periods import PERIODS

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

        with open(file_path, 'w', newline='') as file_csv:
            writer = csv.writer(file_csv, lineterminator='\n')
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

        with open(file_path, 'w', newline='') as file_csv:
            writer = csv.writer(file_csv, lineterminator='\n')
            writer.writerow(headers)
            writer.writerows(rows)

    def write_config_mask_csv(self, mapping, file_path):
        headers = [
            "path",
            "value",
        ]

        rows = []

        for path, rule in mapping.items():
            rows.append([path, rule["value"]])

        with open(file_path, 'w', newline='') as file_csv:
            writer = csv.writer(file_csv, lineterminator='\n')
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
    initial_data = test_docs_tender_below
    initial_config = test_tender_below_config
    docservice = True
    docservice_url = DOCS_URL
    auctions_url = AUCTIONS_URL

    whitelist = ('/openprocurement/.*models.*',)
    blacklist = (r'/tests/.*\.py',)

    def setUp(self):
        super().setUp()
        self.setUpMock()

    def tearDown(self):
        self.tearDownMock()
        super().tearDown()

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
            '/tenders/{}/criteria?acc_token={}'.format(tender_id, owner_token), {'data': test_criteria_data}
        )
        self.assertEqual(response.status, '201 Created')

    def activating_contract(self, contract_id, owner_token, bid_token):
        response = self.app.put_json(
            f'/contracts/{contract_id}/buyer/signer_info?acc_token={owner_token}', {"data": test_signer_info}
        )
        self.assertEqual(response.status, '200 OK')

        response = self.app.put_json(
            f'/contracts/{contract_id}/suppliers/signer_info?acc_token={bid_token}', {"data": test_signer_info}
        )

        self.assertEqual(response.status, '200 OK')
        response = self.app.patch_json(
            f'/contracts/{contract_id}?acc_token={owner_token}',
            {
                'data': {
                    'status': 'active',
                    "contractNumber": "contract #13111",
                    "period": {
                        "startDate": datetime.datetime(year=parse(MOCK_DATETIME).year, month=11, day=1).isoformat(),
                        "endDate": datetime.datetime(year=parse(MOCK_DATETIME).year, month=12, day=31).isoformat(),
                    },
                }
            },
        )
        self.assertEqual(response.status, '200 OK')


class TenderHasAuctionResourceTest(TenderConfigBaseResourceTest):
    initial_config = test_tender_open_config

    def test_docs_has_auction_values_csv(self):
        self.write_config_values_csv(
            config_name="hasAuction",
            file_path=TARGET_CSV_DIR + "has-auction-values.csv",
        )

    def test_docs_has_auction_true(self):
        config = deepcopy(self.initial_config)
        config["hasAuction"] = True

        test_tender_data = deepcopy(test_docs_tender_open)

        lot1 = deepcopy(test_docs_lots[0])
        lot1['value'] = test_tender_data['value']
        lot1['minimalStep'] = test_tender_data['minimalStep']
        lot_id1 = lot1['id'] = uuid4().hex

        lot2 = deepcopy(test_docs_lots[0])
        lot2['value'] = test_tender_data['value']
        lot2['minimalStep'] = test_tender_data['minimalStep']

        test_tender_data['lots'] = [lot1]
        for milestone in test_tender_data["milestones"]:
            milestone["relatedLot"] = lot_id1

        self.app.authorization = ('Basic', ('broker', ''))

        #### Creating tender

        with open(TARGET_DIR + 'has-auction-true-tender-post.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders?opt_pretty=1', {'data': test_tender_data, 'config': config})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        self.app.authorization = ('Basic', ('broker', ''))

        # add lots
        with open(TARGET_DIR + 'has-auction-true-tender-add-lot.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token), {'data': lot2}
            )
            self.assertEqual(response.status, '201 Created')
            lot_id2 = response.json['data']['id']

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = lot_id1
        items[1]["relatedLot"] = lot_id2
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token), {"data": {"items": items}}
        )
        self.assertEqual(response.status, '200 OK')

        self.add_criteria(tender_id, owner_token)
        self.activate_tender(tender_id, owner_token)
        bid1_id, bid1_token, bid2_id, bid2_token = self.register_bids(tender_id, owner_token, lot_id1, lot_id2)

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
            'bids': [
                {
                    "id": bid1_id,
                    "lotValues": [
                        {"participationUrl": '{}?key_for_bid={}'.format(auction1_url, bid1_id)},
                        {"participationUrl": '{}?key_for_bid={}'.format(auction2_url, bid1_id)},
                    ],
                },
                {
                    "id": bid2_id,
                    "lotValues": [
                        {"participationUrl": '{}?key_for_bid={}'.format(auction1_url, bid2_id)},
                        {"participationUrl": '{}?key_for_bid={}'.format(auction2_url, bid2_id)},
                    ],
                },
            ],
        }
        response = self.app.patch_json(
            '/tenders/{}/auction/{}?acc_token={}'.format(self.tender_id, lot_id1, owner_token), {'data': patch_data}
        )
        self.assertEqual(response.status, '200 OK')
        response = self.app.patch_json(
            '/tenders/{}/auction/{}?acc_token={}'.format(self.tender_id, lot_id2, owner_token), {'data': patch_data}
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
                            "id": b["id"],
                            "lotValues": [{"value": l["value"], "relatedLot": l["relatedLot"]} for l in b["lotValues"]],
                        }
                        for b in auction_bids_data
                    ]
                }
            },
        )
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        response = self.app.post_json(
            '/tenders/{}/auction/{}'.format(self.tender_id, lot_id2),
            {
                'data': {
                    'bids': [
                        {
                            "id": b["id"],
                            "lotValues": [{"value": l["value"], "relatedLot": l["relatedLot"]} for l in b["lotValues"]],
                        }
                        for b in auction_bids_data
                    ]
                }
            },
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
        config = deepcopy(self.initial_config)
        config["hasAuction"] = False

        test_tender_data = deepcopy(test_docs_tender_open)
        del test_tender_data['minimalStep']
        lot1 = deepcopy(test_docs_lots[0])
        lot1['value'] = test_tender_data['value']
        lot_id1 = lot1['id'] = uuid4().hex

        lot2 = deepcopy(test_docs_lots[0])
        lot2['value'] = test_tender_data['value']

        test_tender_data['lots'] = [lot1]

        for milestone in test_tender_data["milestones"]:
            milestone["relatedLot"] = lot_id1

        #### Creating tender

        with open(TARGET_DIR + 'has-auction-false-tender-post.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders?opt_pretty=1', {'data': test_tender_data, 'config': config})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        self.app.authorization = ('Basic', ('broker', ''))

        # add lots
        with open(TARGET_DIR + 'has-auction-false-tender-add-lot.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token), {'data': lot2}
            )
            self.assertEqual(response.status, '201 Created')
            lot_id2 = response.json['data']['id']

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = lot_id1
        items[1]["relatedLot"] = lot_id2
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token), {"data": {"items": items}}
        )
        self.assertEqual(response.status, '200 OK')

        self.add_criteria(tender_id, owner_token)
        self.activate_tender(tender_id, owner_token)
        bid1_id, bid1_token, bid2_id, bid2_token = self.register_bids(tender_id, owner_token, lot_id1, lot_id2)

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
        self.add_notice_doc(tender_id, owner_token)
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token), {'data': {"status": "active.tendering"}}
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
                    'lotValues': [
                        {
                            "subcontractingDetails": "ДКП «Орфей», Україна",
                            "value": {"amount": 500},
                            'relatedLot': lot_id1,
                        },
                        {
                            "subcontractingDetails": "ДКП «Орфей», Україна",
                            "value": {"amount": 500},
                            'relatedLot': lot_id2,
                        },
                    ],
                }
            },
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
                    'lotValues': [
                        {
                            "subcontractingDetails": "ДКП «Укр Прінт», Україна",
                            "value": {"amount": 500},
                            'relatedLot': lot_id1,
                        },
                        {
                            "subcontractingDetails": "ДКП «Укр Прінт», Україна",
                            "value": {"amount": 500},
                            'relatedLot': lot_id2,
                        },
                    ],
                }
            },
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
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award2_id, owner_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )

        #### Bypass complaintPeriod
        tender = self.mongodb.tenders.get(self.tender_id)
        for i in tender.get('awards', []):
            if "complaintPeriod" in i:
                i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.mongodb.tenders.save(tender)

        #### Activating contract
        response = self.app.get('/tenders/{}/contracts?acc_token={}'.format(self.tender_id, owner_token))

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
            'lotValues': [
                {"value": {"amount": 300}, 'relatedLot': lot_id1},
                {"value": {"amount": 500}, 'relatedLot': lot_id2},
            ],
        }
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid_data})
        self.assertEqual(response.status, '201 Created')
        bid1_id = response.json['data']['id']
        bid1_token = response.json['access']['token']
        self.set_responses(tender_id, response.json, "pending")

        bid_data["lotValues"][0]["value"]["amount"] = 500
        bid_data["lotValues"][1]["value"]["amount"] = 400
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid_data})
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
        test_tender_data["items"] = deepcopy(test_docs_items_open)
        lot1 = deepcopy(test_docs_lots[0])
        lot1['value'] = test_tender_data['value']
        lot1['minimalStep'] = test_tender_data['minimalStep']
        lot_id1 = lot1['id'] = uuid4().hex

        lot2 = deepcopy(test_docs_lots[0])
        lot2['value'] = test_tender_data['value']
        lot2['minimalStep'] = test_tender_data['minimalStep']

        test_tender_data['lots'] = [lot1]
        for milestone in test_tender_data["milestones"]:
            milestone["relatedLot"] = lot_id1

        # Creating tender

        with open(TARGET_DIR + 'has-awarding-order-true-tender-post.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders?opt_pretty=1', {'data': test_tender_data, 'config': config})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        self.app.authorization = ('Basic', ('broker', ''))

        # add lots
        with open(TARGET_DIR + 'has-awarding-order-true-tender-add-lot.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token), {'data': lot2}
            )
            self.assertEqual(response.status, '201 Created')
            lot_id2 = response.json['data']['id']

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = lot_id1
        items[1]["relatedLot"] = lot_id2
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token), {"data": {"items": items}}
        )
        self.assertEqual(response.status, '200 OK')

        self.add_criteria(tender_id, owner_token)
        # Tender activating

        self.add_notice_doc(tender_id, owner_token)
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token), {'data': {"status": "active.enquiries"}}
        )
        self.assertEqual(response.status, '200 OK')

        # enquires
        response = self.app.post_json(
            '/tenders/{}/questions'.format(tender_id), {"data": test_docs_question}, status=201
        )
        question_id = response.json['data']['id']
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json(
            '/tenders/{}/questions/{}?acc_token={}'.format(tender_id, question_id, owner_token),
            {"data": {"answer": "Таблицю додано в файлі \"Kalorijnist.xslx\""}},
            status=200,
        )
        self.assertEqual(response.status, '200 OK')
        self.set_status('active.tendering')
        bid1_id, bid1_token, bid2_id, bid2_token = self.register_bids(tender_id, lot_id1, lot_id2)

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
            'bids': [
                {
                    "id": bid1_id,
                    "lotValues": [
                        {"participationUrl": '{}?key_for_bid={}'.format(auction1_url, bid1_id)},
                        {"participationUrl": '{}?key_for_bid={}'.format(auction2_url, bid1_id)},
                    ],
                },
                {
                    "id": bid2_id,
                    "lotValues": [
                        {"participationUrl": '{}?key_for_bid={}'.format(auction1_url, bid2_id)},
                        {"participationUrl": '{}?key_for_bid={}'.format(auction2_url, bid2_id)},
                    ],
                },
            ],
        }
        response = self.app.patch_json(
            '/tenders/{}/auction/{}?acc_token={}'.format(self.tender_id, lot_id1, owner_token), {'data': patch_data}
        )
        self.assertEqual(response.status, '200 OK')
        response = self.app.patch_json(
            '/tenders/{}/auction/{}?acc_token={}'.format(self.tender_id, lot_id2, owner_token), {'data': patch_data}
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
                            "id": b["id"],
                            "lotValues": [{"value": l["value"], "relatedLot": l["relatedLot"]} for l in b["lotValues"]],
                        }
                        for b in auction_bids_data
                    ]
                }
            },
        )
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        self.app.post_json(
            '/tenders/{}/auction/{}'.format(self.tender_id, lot_id2),
            {
                'data': {
                    'bids': [
                        {
                            "id": b["id"],
                            "lotValues": [{"value": l["value"], "relatedLot": l["relatedLot"]} for l in b["lotValues"]],
                        }
                        for b in auction_bids_data
                    ]
                }
            },
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
        test_tender_data["items"] = deepcopy(test_docs_items_open)
        lot1 = deepcopy(test_docs_lots[0])
        lot1['value'] = test_tender_data['value']
        lot1['minimalStep'] = test_tender_data['minimalStep']
        lot_id1 = lot1['id'] = uuid4().hex

        lot2 = deepcopy(test_docs_lots[0])
        lot2['value'] = test_tender_data['value']
        lot2['minimalStep'] = test_tender_data['minimalStep']

        test_tender_data['lots'] = [lot1]
        for milestone in test_tender_data["milestones"]:
            milestone["relatedLot"] = lot_id1

        # Creating tender

        with open(TARGET_DIR + 'has-awarding-order-false-tender-post.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders?opt_pretty=1', {'data': test_tender_data, 'config': config})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        self.app.authorization = ('Basic', ('broker', ''))

        # add lots
        with open(TARGET_DIR + 'has-awarding-order-false-tender-add-lot.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token), {'data': lot2}
            )
            self.assertEqual(response.status, '201 Created')
            lot_id2 = response.json['data']['id']

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = lot_id1
        items[1]["relatedLot"] = lot_id2

        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token), {"data": {"items": items}}
        )
        self.assertEqual(response.status, '200 OK')

        self.add_criteria(tender_id, owner_token)
        # Tender activating

        self.add_notice_doc(tender_id, owner_token)
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token), {'data': {"status": "active.enquiries"}}
        )
        self.assertEqual(response.status, '200 OK')

        # enquires
        response = self.app.post_json(
            '/tenders/{}/questions'.format(tender_id), {"data": test_docs_question}, status=201
        )
        question_id = response.json['data']['id']
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json(
            '/tenders/{}/questions/{}?acc_token={}'.format(tender_id, question_id, owner_token),
            {"data": {"answer": "Таблицю додано в файлі \"Kalorijnist.xslx\""}},
            status=200,
        )
        self.assertEqual(response.status, '200 OK')
        self.set_status('active.tendering')
        bid1_id, bid1_token, bid2_id, bid2_token = self.register_bids(tender_id, lot_id1, lot_id2)

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
            'bids': [
                {
                    "id": bid1_id,
                    "lotValues": [
                        {"participationUrl": '{}?key_for_bid={}'.format(auction1_url, bid1_id)},
                        {"participationUrl": '{}?key_for_bid={}'.format(auction2_url, bid1_id)},
                    ],
                },
                {
                    "id": bid2_id,
                    "lotValues": [
                        {"participationUrl": '{}?key_for_bid={}'.format(auction1_url, bid2_id)},
                        {"participationUrl": '{}?key_for_bid={}'.format(auction2_url, bid2_id)},
                    ],
                },
            ],
        }
        response = self.app.patch_json(
            '/tenders/{}/auction/{}?acc_token={}'.format(self.tender_id, lot_id1, owner_token), {'data': patch_data}
        )
        self.assertEqual(response.status, '200 OK')
        response = self.app.patch_json(
            '/tenders/{}/auction/{}?acc_token={}'.format(self.tender_id, lot_id2, owner_token), {'data': patch_data}
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
                            "id": b["id"],
                            "lotValues": [{"value": l["value"], "relatedLot": l["relatedLot"]} for l in b["lotValues"]],
                        }
                        for b in auction_bids_data
                    ]
                }
            },
        )
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        self.app.post_json(
            '/tenders/{}/auction/{}'.format(self.tender_id, lot_id2),
            {
                'data': {
                    'bids': [
                        {
                            "id": b["id"],
                            "lotValues": [{"value": l["value"], "relatedLot": l["relatedLot"]} for l in b["lotValues"]],
                        }
                        for b in auction_bids_data
                    ]
                }
            },
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
        response = self.app.post_json('/tenders?opt_pretty=1', {'data': test_tender_data, 'config': config})
        self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']
        lots = response.json['data']["lots"]
        lot_id = lots[0]["id"]

        self.app.authorization = ('Basic', ('broker', ''))
        self.add_criteria(tender_id, owner_token)

        # Tender activating
        self.add_notice_doc(tender_id, owner_token)
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token), {'data': {"status": "active.enquiries"}}
        )
        self.assertEqual(response.status, '200 OK')

        # enquires
        response = self.app.post_json(
            '/tenders/{}/questions'.format(tender_id), {"data": test_docs_question}, status=201
        )
        question_id = response.json['data']['id']
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json(
            '/tenders/{}/questions/{}?acc_token={}'.format(tender_id, question_id, owner_token),
            {"data": {"answer": "Таблицю додано в файлі \"Kalorijnist.xslx\""}},
            status=200,
        )
        self.assertEqual(response.status, '200 OK')
        self.set_status('active.tendering')

        # register bids
        bids = []
        bids_tokens = []
        for idx in range(3):
            self.app.authorization = ('Basic', ('broker', ''))
            bid_data = {'status': 'draft', 'tenderers': test_docs_bid["tenderers"], "value": {"amount": 500 - idx}}
            set_bid_lotvalues(bid_data, lots)
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid_data})
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
            'bids': [
                {"id": bids[0], "lotValues": [{"participationUrl": '{}?key_for_bid={}'.format(auction_url, bids[0])}]},
                {
                    "id": bids[1],
                    "lotValues": [
                        {"participationUrl": '{}?key_for_bid={}'.format(auction_url, bids[1])},
                    ],
                },
                {
                    "id": bids[2],
                    "lotValues": [
                        {"participationUrl": '{}?key_for_bid={}'.format(auction_url, bids[2])},
                    ],
                },
            ],
        }
        response = self.app.patch_json(
            '/tenders/{}/auction/{}?acc_token={}'.format(self.tender_id, lot_id, owner_token), {'data': patch_data}
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
                                {"value": lot["value"], "relatedLot": lot["relatedLot"]} for lot in b["lotValues"]
                            ],
                        }
                        for b in auction_bids_data
                    ]
                }
            },
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
        with open(
            TARGET_DIR + 'has-awarding-order-false-auction-results-example-1-activate-first-award.http', 'w'
        ) as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_1_id, owner_token),
                {'data': {'status': 'active'}},
            )
            self.assertEqual(response.status, '200 OK')

        with open(
            TARGET_DIR + 'has-awarding-order-false-auction-results-example-1-results.http', 'w'
        ) as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token),
            )
            self.assertEqual(response.status, '200 OK')

        # The customer cancels decision due to award1
        with open(
            TARGET_DIR + 'has-awarding-order-false-auction-results-example-2-cancel-first-award.http', 'w'
        ) as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_1_id, owner_token),
                {'data': {'status': 'cancelled'}},
            )
            self.assertEqual(response.status, '200 OK')

        with open(
            TARGET_DIR + 'has-awarding-order-false-auction-results-example-2-results.http', 'w'
        ) as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token),
            )
            self.assertEqual(response.status, '200 OK')
            award_4_id = response.json["data"][-1]["id"]

        # The customer rejects award4 (1.1) and recognizes as the winner award2
        response = self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_4_id, owner_token),
            {'data': {'status': 'unsuccessful'}},
        )
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_2_id, owner_token),
            {'data': {'status': 'active'}},
        )
        self.assertEqual(response.status, '200 OK')

        with open(
            TARGET_DIR + 'has-awarding-order-false-auction-results-example-3-results.http', 'w'
        ) as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token),
            )
            self.assertEqual(response.status, '200 OK')

        claim = deepcopy(test_docs_claim)
        claim_data = {'data': claim}
        claim_data['data']['status'] = 'claim'
        response = self.app.post_json(
            '/tenders/{}/awards/{}/complaints?acc_token={}'.format(self.tender_id, award_4_id, bids_tokens[0]),
            claim_data,
        )
        self.assertEqual(response.status, '201 Created')

        complaint_token = response.json['access']['token']
        complaint_id = response.json['data']['id']

        response = self.app.patch_json(
            '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                self.tender_id, award_4_id, complaint_id, owner_token
            ),
            {
                'data': {
                    "status": "answered",
                    "resolutionType": "resolved",
                    "resolution": "Умови виправлено, вибір переможня буде розгянуто повторно",
                }
            },
        )
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/awards/{}/complaints/{}?acc_token={}'.format(
                self.tender_id, award_4_id, complaint_id, complaint_token
            ),
            {
                'data': {
                    "satisfied": True,
                }
            },
        )
        self.assertEqual(response.status, '200 OK')

        # The customer cancel unsuccessful award4
        self.assertEqual(response.status, '200 OK')
        response = self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_4_id, owner_token),
            {'data': {'status': 'cancelled'}},
        )
        self.assertEqual(response.status, '200 OK')

        with open(
            TARGET_DIR + 'has-awarding-order-false-auction-results-example-4-results.http', 'w'
        ) as self.app.file_obj:
            response = self.app.get(
                '/tenders/{}/awards?acc_token={}'.format(self.tender_id, owner_token),
            )
            self.assertEqual(response.status, '200 OK')


class TenderHasValueEstimationResourceTest(TenderConfigBaseResourceTest):
    def test_docs_has_value_estimation_values_csv(self):
        self.write_config_values_csv(
            config_name="hasValueEstimation",
            file_path=TARGET_CSV_DIR + "has-value-estimation-values.csv",
        )

    def test_docs_lots_has_value_estimation_true(self):
        config = deepcopy(self.initial_config)
        config["hasValueEstimation"] = True
        test_tender_data = deepcopy(test_docs_tender_below)
        test_tender_data["items"] = deepcopy(test_docs_items_open)

        with open(TARGET_DIR + 'has-value-estimation-true-tender-lots-post.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders?opt_pretty=1', {'data': test_tender_data, 'config': config})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        test_lots = deepcopy(test_docs_lots)
        test_lots[0]['value'] = test_tender_data['value']
        test_lots[0]['minimalStep'] = test_tender_data['minimalStep']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        self.app.authorization = ('Basic', ('broker', ''))

        # add lots
        with open(TARGET_DIR + 'has-value-estimation-true-tender-lots-add-post.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                {'data': test_lots[0]},
            )
            self.assertEqual(response.status, '201 Created')

        # get complete tender
        with open(TARGET_DIR + 'has-value-estimation-true-tender-complete.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender_id))
            self.assertEqual(response.status, '200 OK')

    def test_docs_lots_has_value_estimation_false(self):
        config = deepcopy(self.initial_config)
        config["hasValueEstimation"] = False
        config["hasValueRestriction"] = False

        test_tender_data = deepcopy(test_docs_tender_below)
        test_tender_data["items"] = deepcopy(test_docs_items_open)
        with open(TARGET_DIR + 'has-value-estimation-false-tender-lots-post-invalid.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1', {'data': test_tender_data, 'config': config}, status=422
            )
            self.assertEqual(response.status, "422 Unprocessable Entity")

        test_tender_data["value"]["amount"] = 0
        with open(TARGET_DIR + 'has-value-estimation-false-tender-lots-post.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders?opt_pretty=1', {'data': test_tender_data, 'config': config})
            self.assertEqual(response.status, "201 Created")

        tender = response.json['data']
        test_lots = deepcopy(test_docs_lots)
        test_lots[0]['value'] = test_tender_data['value']
        test_lots[0]['minimalStep'] = test_tender_data['minimalStep']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        self.app.authorization = ('Basic', ('broker', ''))

        # add lots invalid
        test_lots[0]['value']["amount"] = 100
        with open(
            TARGET_DIR + 'has-value-estimation-false-tender-lots-add-post-invalid.http', 'w'
        ) as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token), {'data': test_lots[0]}, status=422
            )
            self.assertEqual(response.status, '422 Unprocessable Entity')

        test_lots[0]['value']["amount"] = 0
        # add lots
        with open(TARGET_DIR + 'has-value-estimation-false-tender-lots-add-post.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token),
                {'data': test_lots[0]},
            )
            self.assertEqual(response.status, '201 Created')

        # get complete tender
        with open(TARGET_DIR + 'has-value-estimation-false-tender-complete.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender_id))
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
        test_tender_data["items"] = deepcopy(test_docs_items_open)
        lot1 = deepcopy(test_docs_lots[0])
        lot1['value'] = test_tender_data['value']
        lot1['minimalStep'] = test_tender_data['minimalStep']
        lot_id1 = lot1['id'] = uuid4().hex

        lot2 = deepcopy(test_docs_lots[1])
        lot2['value'] = test_tender_data['value']
        lot2['minimalStep'] = test_tender_data['minimalStep']
        lot_id2 = lot2['id'] = uuid4().hex

        test_tender_data['lots'] = [lot1, lot2]
        for item in test_tender_data["items"]:
            item["relatedLot"] = lot_id1
        for milestone in test_tender_data["milestones"]:
            milestone["relatedLot"] = lot_id1

        #### Creating tender

        with open(TARGET_DIR + 'has-value-restriction-true-tender-lots-post.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders?opt_pretty=1', {'data': test_tender_data, 'config': config})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        self.add_criteria(tender_id, owner_token)

        # Tender activating
        self.add_notice_doc(tender_id, owner_token)
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token), {'data': {"status": "active.enquiries"}}
        )
        self.assertEqual(response.status, '200 OK')

        # enquires
        response = self.app.post_json(
            '/tenders/{}/questions'.format(tender_id), {"data": test_docs_question}, status=201
        )
        question_id = response.json['data']['id']
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json(
            '/tenders/{}/questions/{}?acc_token={}'.format(tender_id, question_id, owner_token),
            {"data": {"answer": "Таблицю додано в файлі \"Kalorijnist.xslx\""}},
            status=200,
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
                        'lotValues': [
                            {"value": {"amount": 600}, 'relatedLot': lot_id1},
                            {"value": {"amount": 500}, 'relatedLot': lot_id2},
                        ],
                    }
                },
                status=422,
            )
            self.assertEqual(response.status, "422 Unprocessable Entity")
            self.assertEqual(
                response.json["errors"],
                [
                    {
                        "location": "body",
                        "name": "lotValues",
                        "description": [{"value": ["value of bid should be less than value of lot"]}],
                    }
                ],
            )

        with open(TARGET_DIR + 'has-value-restriction-true-tender-lots-add-valid-bid.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f'/tenders/{tender_id}/bids',
                {
                    'data': {
                        'status': 'draft',
                        'tenderers': test_docs_bid["tenderers"],
                        'lotValues': [
                            {"value": {"amount": 500}, 'relatedLot': lot_id1},
                            {"value": {"amount": 500}, 'relatedLot': lot_id2},
                        ],
                    }
                },
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
                        'lotValues': [
                            {"value": {"amount": 500}, 'relatedLot': lot_id1},
                            {"value": {"amount": 700}, 'relatedLot': lot_id2},
                        ],
                    }
                },
                status=422,
            )
            self.assertEqual(response.status, "422 Unprocessable Entity")
            self.assertEqual(
                response.json["errors"],
                [
                    {
                        "location": "body",
                        "name": "lotValues",
                        "description": [{"value": ["value of bid should be less than value of lot"]}],
                    }
                ],
            )

    def test_docs_lots_has_value_restriction_false(self):
        config = deepcopy(self.initial_config)
        config["hasValueRestriction"] = False

        test_tender_data = deepcopy(test_docs_tender_below)
        test_tender_data["items"] = deepcopy(test_docs_items_open)
        lot1 = deepcopy(test_docs_lots[0])
        lot1['value'] = test_tender_data['value']
        lot1['minimalStep'] = test_tender_data['minimalStep']
        lot_id1 = lot1['id'] = uuid4().hex

        lot2 = deepcopy(test_docs_lots[1])
        lot2['value'] = test_tender_data['value']
        lot2['minimalStep'] = test_tender_data['minimalStep']
        lot_id2 = lot2['id'] = uuid4().hex

        test_tender_data['lots'] = [lot1, lot2]
        for item in test_tender_data["items"]:
            item["relatedLot"] = lot_id1
        for milestone in test_tender_data["milestones"]:
            milestone["relatedLot"] = lot_id1

        #### Creating tender

        with open(TARGET_DIR + 'has-value-restriction-false-tender-lots-post.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders?opt_pretty=1', {'data': test_tender_data, 'config': config})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        self.add_criteria(tender_id, owner_token)

        # Tender activating
        self.add_notice_doc(tender_id, owner_token)
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token), {'data': {"status": "active.enquiries"}}
        )
        self.assertEqual(response.status, '200 OK')

        # enquires
        response = self.app.post_json(
            '/tenders/{}/questions'.format(tender_id), {"data": test_docs_question}, status=201
        )
        question_id = response.json['data']['id']
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json(
            '/tenders/{}/questions/{}?acc_token={}'.format(tender_id, question_id, owner_token),
            {"data": {"answer": "Таблицю додано в файлі \"Kalorijnist.xslx\""}},
            status=200,
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
                        'lotValues': [
                            {"value": {"amount": 600}, 'relatedLot': lot_id1},
                            {"value": {"amount": 700}, 'relatedLot': lot_id2},
                        ],
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
        lot1 = deepcopy(test_docs_lots[0])
        lot1['value'] = test_tender_data['value']
        lot1['minimalStep'] = test_tender_data['minimalStep']
        lot_id1 = lot1['id'] = uuid4().hex

        lot2 = deepcopy(test_docs_lots[1])
        lot2['value'] = test_tender_data['value']
        lot2['minimalStep'] = test_tender_data['minimalStep']
        lot_id2 = lot2['id'] = uuid4().hex

        test_tender_data['lots'] = [lot1, lot2]
        for item in test_tender_data["items"]:
            item["relatedLot"] = lot_id1
        for milestone in test_tender_data["milestones"]:
            milestone["relatedLot"] = lot_id1

        # Creating tender

        with open(TARGET_DIR + 'value-currency-equality-true-tender-lots-post.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders?opt_pretty=1', {'data': test_tender_data, 'config': config})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        self.add_criteria(tender_id, owner_token)

        # Tender activating
        self.add_notice_doc(tender_id, owner_token)
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token), {'data': {"status": "active.enquiries"}}
        )
        self.assertEqual(response.status, '200 OK')

        # enquires
        response = self.app.post_json(
            '/tenders/{}/questions'.format(tender_id), {"data": test_docs_question}, status=201
        )
        question_id = response.json['data']['id']
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json(
            '/tenders/{}/questions/{}?acc_token={}'.format(tender_id, question_id, owner_token),
            {"data": {"answer": "Таблицю додано в файлі \"Kalorijnist.xslx\""}},
            status=200,
        )
        self.assertEqual(response.status, '200 OK')
        self.set_status('active.tendering')

        # Registering bid

        with open(
            TARGET_DIR + 'value-currency-equality-true-tender-lots-add-invalid-bid.http', 'w'
        ) as self.app.file_obj:
            response = self.app.post_json(
                f'/tenders/{tender_id}/bids',
                {
                    'data': {
                        'status': 'draft',
                        'tenderers': test_docs_bid["tenderers"],
                        'lotValues': [
                            {"value": {"amount": 600, "currency": "USD"}, 'relatedLot': lot_id1},
                            {"value": {"amount": 500, "currency": "UAH"}, 'relatedLot': lot_id2},
                        ],
                    }
                },
                status=422,
            )
            self.assertEqual(response.status, "422 Unprocessable Entity")
            self.assertEqual(
                response.json["errors"],
                [
                    {
                        "location": "body",
                        "name": "lotValues",
                        "description": [{"value": ["currency of bid should be identical to currency of value of lot"]}],
                    }
                ],
            )

        with open(TARGET_DIR + 'value-currency-equality-true-tender-lots-add-valid-bid.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                f'/tenders/{tender_id}/bids',
                {
                    'data': {
                        'status': 'draft',
                        'tenderers': test_docs_bid["tenderers"],
                        'lotValues': [
                            {"value": {"amount": 500, "currency": "UAH"}, 'relatedLot': lot_id1},
                            {"value": {"amount": 500, "currency": "UAH"}, 'relatedLot': lot_id2},
                        ],
                    }
                },
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
                        'lotValues': [
                            {"value": {"amount": 500, "currency": "UAH"}, 'relatedLot': lot_id1},
                            {"value": {"amount": 700, "currency": "USD"}, 'relatedLot': lot_id2},
                        ],
                    }
                },
                status=422,
            )
            self.assertEqual(response.status, "422 Unprocessable Entity")
            self.assertEqual(
                response.json["errors"],
                [
                    {
                        "location": "body",
                        "name": "lotValues",
                        "description": [{"value": ["currency of bid should be identical to currency of value of lot"]}],
                    }
                ],
            )

    def test_docs_lots_value_currency_equality_false(self):
        config = deepcopy(self.initial_config)
        config.update(
            {
                "valueCurrencyEquality": False,
                "hasAuction": False,
                "hasAwardingOrder": False,
                "hasValueRestriction": False,
            }
        )

        test_tender_data = deepcopy(test_docs_tender_below)
        test_tender_data["items"] = deepcopy(test_docs_items_open)
        del test_tender_data["minimalStep"]
        lot1 = deepcopy(test_docs_lots[0])
        lot1['value'] = test_tender_data['value']
        lot_id1 = lot1['id'] = uuid4().hex

        lot2 = deepcopy(test_docs_lots[1])
        lot2['value'] = test_tender_data['value']
        lot_id2 = lot2['id'] = uuid4().hex

        test_tender_data['lots'] = [lot1, lot2]
        for item in test_tender_data["items"]:
            item["relatedLot"] = lot_id1
        for milestone in test_tender_data["milestones"]:
            milestone["relatedLot"] = lot_id1

        # Creating tender

        with open(TARGET_DIR + 'value-currency-equality-false-tender-lots-post.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders?opt_pretty=1', {'data': test_tender_data, 'config': config})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        self.add_criteria(tender_id, owner_token)

        # Tender activating
        self.add_notice_doc(tender_id, owner_token)
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token), {'data': {"status": "active.enquiries"}}
        )
        self.assertEqual(response.status, '200 OK')

        # enquires
        response = self.app.post_json(
            '/tenders/{}/questions'.format(tender_id), {"data": test_docs_question}, status=201
        )
        question_id = response.json['data']['id']
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json(
            '/tenders/{}/questions/{}?acc_token={}'.format(tender_id, question_id, owner_token),
            {"data": {"answer": "Таблицю додано в файлі \"Kalorijnist.xslx\""}},
            status=200,
        )
        self.assertEqual(response.status, '200 OK')
        self.set_status('active.tendering')

        # Registering bid
        with open(
            TARGET_DIR + 'value-currency-equality-false-tender-lots-add-valid-bid.http', 'w'
        ) as self.app.file_obj:
            response = self.app.post_json(
                f'/tenders/{tender_id}/bids',
                {
                    'data': {
                        'status': 'draft',
                        'tenderers': test_docs_bid["tenderers"],
                        'lotValues': [
                            {"value": {"amount": 600, "currency": "USD"}, 'relatedLot': lot_id1},
                            {"value": {"amount": 700, "currency": "EUR"}, 'relatedLot': lot_id2},
                        ],
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
            },
        )
        self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award2_id, owner_token),
            {
                "data": {
                    "status": "active",
                    "qualified": True,
                }
            },
        )

        # Bypass complaintPeriod
        tender = self.mongodb.tenders.get(self.tender_id)
        for i in tender.get('awards', []):
            if "complaintPeriod" in i:
                i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.mongodb.tenders.save(tender)

        # Activating contract
        response = self.app.get('/tenders/{}/contracts?acc_token={}'.format(self.tender_id, owner_token))
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
        self.add_notice_doc(tender_id, owner_token)
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token), {'data': {"status": "active.enquiries"}}
        )
        self.assertEqual(response.status, '200 OK')

        # enquires
        response = self.app.post_json(
            '/tenders/{}/questions'.format(tender_id), {"data": test_docs_question}, status=201
        )
        question_id = response.json['data']['id']
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json(
            '/tenders/{}/questions/{}?acc_token={}'.format(tender_id, question_id, owner_token),
            {"data": {"answer": "Таблицю додано в файлі \"Kalorijnist.xslx\""}},
            status=200,
        )
        self.assertEqual(response.status, '200 OK')
        self.set_status('active.tendering')

    def register_bid(self, tender_id, lot_ids, initial_amount=300):
        bid_data = {'status': 'draft', 'tenderers': test_docs_bid["tenderers"], 'lotValues': []}
        for idx, lot_id in enumerate(lot_ids):
            bid_data["lotValues"].append({"value": {"amount": idx * 100 + initial_amount}, 'relatedLot': lot_id})
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid_data})
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
                [{"location": "body", "name": "minBidsNumber", "description": "0 is less than the minimum of 1"}],
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
                [{"location": "body", "name": "minBidsNumber", "description": "10 is greater than the maximum of 9"}],
            )

    def test_docs_min_bids_number_tendering_unsuccessful(self):
        config = deepcopy(self.initial_config)
        config["minBidsNumber"] = 2
        config["hasValueRestriction"] = True

        test_tender_data = deepcopy(self.initial_data)
        lot = deepcopy(test_docs_lots[0])
        lot['value'] = test_tender_data['value']
        lot['minimalStep'] = test_tender_data['minimalStep']
        lot_id = lot['id'] = uuid4().hex

        test_tender_data['lots'] = [lot]
        for item in test_tender_data["items"]:
            item["relatedLot"] = lot_id
        for milestone in test_tender_data["milestones"]:
            milestone["relatedLot"] = lot_id

        with open(TARGET_DIR + 'min-bids-number-tender-post-1.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': test_tender_data, 'config': config},
            )
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

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
            '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token), {'data': test_lot}
        )
        self.assertEqual(response.status, '201 Created')
        lot = response.json['data']
        lot_id = lot['id']

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = lot_id
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token), {"data": {"items": items}}
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
        test_tender_data['items'] = deepcopy(test_docs_items_open)

        lot1 = deepcopy(test_docs_lots[0])
        lot1['value'] = test_tender_data['value']
        lot1['minimalStep'] = test_tender_data['minimalStep']
        lot_id1 = lot1['id'] = uuid4().hex

        lot2 = deepcopy(test_docs_lots[1])
        lot2['value'] = test_tender_data['value']
        lot2['minimalStep'] = test_tender_data['minimalStep']
        lot_id2 = lot2['id'] = uuid4().hex

        test_tender_data['lots'] = [lot1, lot2]
        for item in test_tender_data["items"]:
            item["relatedLot"] = lot_id1
        for milestone in test_tender_data["milestones"]:
            milestone["relatedLot"] = lot_id1

        with open(TARGET_DIR + 'min-bids-number-tender-post-3.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': test_tender_data, 'config': config},
            )
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

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
            'bids': [
                {
                    "id": bid1_id,
                    "lotValues": [
                        {"participationUrl": '{}?key_for_bid={}'.format(auction1_url, bid1_id)},
                        {"participationUrl": '{}?key_for_bid={}'.format(auction2_url, bid1_id)},
                    ],
                },
                {
                    "id": bid2_id,
                    "lotValues": [
                        {"participationUrl": '{}?key_for_bid={}'.format(auction1_url, bid2_id)},
                        {"participationUrl": '{}?key_for_bid={}'.format(auction2_url, bid2_id)},
                    ],
                },
            ],
        }
        response = self.app.patch_json(
            '/tenders/{}/auction/{}?acc_token={}'.format(self.tender_id, lot_id1, owner_token), {'data': patch_data}
        )
        self.assertEqual(response.status, '200 OK')
        response = self.app.patch_json(
            '/tenders/{}/auction/{}?acc_token={}'.format(self.tender_id, lot_id2, owner_token), {'data': patch_data}
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
                            "id": b["id"],
                            "lotValues": [{"value": l["value"], "relatedLot": l["relatedLot"]} for l in b["lotValues"]],
                        }
                        for b in auction_bids_data
                    ]
                }
            },
        )
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        self.app.post_json(
            '/tenders/{}/auction/{}'.format(self.tender_id, lot_id2),
            {
                'data': {
                    'bids': [
                        {
                            "id": b["id"],
                            "lotValues": [{"value": l["value"], "relatedLot": l["relatedLot"]} for l in b["lotValues"]],
                        }
                        for b in auction_bids_data
                    ]
                }
            },
        )

        self.app.authorization = ('Basic', ('broker', ''))
        with open(TARGET_DIR + 'min-bids-number-tender-qualification-2.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(self.tender_id))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'active.qualification')


class TenderComplainRegulationResourceTest(TenderConfigBaseResourceTest):
    initial_data = deepcopy(test_docs_tender_below)
    initial_config = deepcopy(test_tender_below_config)

    def test_docs_tender_complain_regulation_values_csv(self):
        self.write_config_values_csv(
            config_name="tenderComplainRegulation",
            file_path=TARGET_CSV_DIR + "tender-complain-regulation-values.csv",
        )

    def test_docs_tender_complain_regulation_complaint_period_exists(self):
        config = deepcopy(test_tender_open_config)
        test_tender_data = deepcopy(test_docs_tender_open)

        # Create tender
        with open(TARGET_DIR + "tender-complain-regulation-tender-post-1.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders?opt_pretty=1",
                {"data": test_tender_data, "config": config},
            )
            self.assertEqual(response.status, "201 Created")

        tender = response.json["data"]
        tender_id = self.tender_id = tender["id"]
        owner_token = response.json["access"]["token"]

        self.app.authorization = ("Basic", ("broker", ""))

        # add lot
        test_lot = deepcopy(test_docs_lots[0])
        test_lot["value"] = test_tender_data["value"]
        test_lot["minimalStep"] = test_tender_data["minimalStep"]
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token),
            {"data": test_lot},
        )
        self.assertEqual(response.status, "201 Created")
        lot = response.json["data"]
        lot_id = lot["id"]

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = lot_id
        with open(TARGET_DIR + "tender-complain-regulation-tender-patch-1.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(tender_id, owner_token),
                {"data": {"items": items}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertIn("complaintPeriod", response.json["data"])

    def test_docs_tender_complain_regulation_complaint_period_dont_exist(self):
        config = deepcopy(self.initial_config)

        # Create tender
        with open(TARGET_DIR + "tender-complain-regulation-tender-post-2.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders?opt_pretty=1",
                {"data": self.initial_data, "config": config},
            )
            self.assertEqual(response.status, "201 Created")

        tender = response.json["data"]
        tender_id = self.tender_id = tender["id"]
        owner_token = response.json["access"]["token"]

        self.app.authorization = ("Basic", ("broker", ""))

        # add lot
        test_lot = deepcopy(test_docs_lots[0])
        test_lot["value"] = self.initial_data["value"]
        test_lot["minimalStep"] = self.initial_data["minimalStep"]
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token),
            {"data": test_lot},
        )
        self.assertEqual(response.status, "201 Created")
        lot = response.json["data"]
        lot_id = lot["id"]

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = lot_id
        with open(TARGET_DIR + "tender-complain-regulation-tender-patch-2.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}?acc_token={}".format(tender_id, owner_token),
                {"data": {"items": items}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertNotIn("complaintPeriod", response.json["data"])


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


class TenderComplaintsResourceTest(TenderConfigBaseResourceTest):
    def test_docs_has_pre_selection_agreement_values_csv(self):
        for config_name in ("hasTenderComplaints", "hasAwardComplaints", "hasCancellationComplaints"):
            self.write_config_values_csv(
                config_name=config_name,
                file_path=TARGET_CSV_DIR + f"{config_name}-values.csv",
            )


class TenderQualificationComplainDurationResourceTest(TenderConfigBaseResourceTest):
    periods = PERIODS

    def test_docs_qualification_complain_duration_values_csv(self):
        self.write_config_values_csv(
            config_name="qualificationComplainDuration",
            file_path=TARGET_CSV_DIR + "qualification-complain-duration-values.csv",
        )

    def test_docs_qualification_complain_duration_5_days(self):
        test_tender_data = deepcopy(test_docs_tender_esco)
        config = deepcopy(test_tender_esco_config)
        test_lots = deepcopy(test_docs_lots)
        bid = deepcopy(test_docs_bid_draft)
        bid2 = deepcopy(test_docs_bid2)
        bid3 = deepcopy(test_docs_bid3_with_docs)

        bid.update(test_docs_subcontracting)
        bid.update(test_docs_qualified)
        bid2.update(test_docs_qualified)
        bid3.update(test_docs_qualified)

        bid.update(
            {
                "value": {
                    "annualCostsReduction": [500] + [1000] * 20,
                    "yearlyPaymentsPercentage": 0.9,
                    "contractDuration": {"years": 10, "days": 74},
                }
            }
        )

        bid2.update(
            {
                "value": {
                    "annualCostsReduction": [400] + [900] * 20,
                    "yearlyPaymentsPercentage": 0.85,
                    "contractDuration": {"years": 12, "days": 200},
                }
            }
        )

        bid3.update(
            {
                "value": {
                    "annualCostsReduction": [200] + [800] * 20,
                    "yearlyPaymentsPercentage": 0.86,
                    "contractDuration": {"years": 13, "days": 40},
                }
            }
        )
        test_lots[0]['minimalStepPercentage'] = test_tender_data['minimalStepPercentage']
        test_lots[1]['minimalStepPercentage'] = test_tender_data['minimalStepPercentage']

        #### Creating tender
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders?opt_pretty=1', {'data': test_tender_data, 'config': config})
        self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        # add lots
        response = self.app.post_json(
            '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token), {'data': test_lots[0]}
        )
        self.assertEqual(response.status, '201 Created')
        lot_id1 = response.json['data']['id']

        response = self.app.post_json(
            '/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token), {'data': test_lots[1]}
        )
        self.assertEqual(response.status, '201 Created')
        lot_id2 = response.json['data']['id']

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = lot_id1
        items[1]["relatedLot"] = lot_id2
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token), {"data": {"items": items}}
        )
        self.assertEqual(response.status, '200 OK')

        #### Tender activating
        test_criteria_data = deepcopy(test_exclusion_criteria)
        test_criteria_data.extend(test_language_criteria)

        response = self.app.post_json(
            f'/tenders/{self.tender_id}/criteria?acc_token={owner_token}', {'data': test_criteria_data}
        )
        self.assertEqual(response.status, '201 Created')

        self.add_notice_doc(tender_id, owner_token)
        response = self.app.patch_json(
            f'/tenders/{self.tender_id}?acc_token={owner_token}', {'data': {'status': 'active.tendering'}}
        )
        self.assertEqual(response.status, '200 OK')

        # Registering bids
        response = self.app.post_json(
            '/tenders/{}/bids'.format(tender_id),
            {
                'data': {
                    'selfQualified': True,
                    'status': 'draft',
                    'tenderers': bid["tenderers"],
                    'lotValues': [
                        {
                            "subcontractingDetails": "ДКП «Орфей», Україна",
                            "value": {
                                'annualCostsReduction': [200] + [1000] * 20,
                                'yearlyPaymentsPercentage': 0.87,
                                'contractDuration': {"years": 7},
                            },
                            'relatedLot': lot_id1,
                        }
                    ],
                }
            },
        )
        self.assertEqual(response.status, '201 Created')
        bid1_token = response.json['access']['token']
        bid1_id = response.json['data']['id']
        self.set_responses(tender_id, response.json, "pending")

        response = self.app.post_json(
            '/tenders/{}/bids'.format(tender_id),
            {
                'data': {
                    'selfQualified': True,
                    'status': 'draft',
                    'tenderers': bid2["tenderers"],
                    'lotValues': [
                        {
                            "value": {
                                'annualCostsReduction': [700] + [1600] * 20,
                                'yearlyPaymentsPercentage': 0.9,
                                'contractDuration': {"years": 7},
                            },
                            'relatedLot': lot_id1,
                        },
                        {
                            "subcontractingDetails": "ДКП «Укр Прінт», Україна",
                            "value": {
                                'annualCostsReduction': [600] + [1200] * 20,
                                'yearlyPaymentsPercentage': 0.96,
                                'contractDuration': {"years": 9},
                            },
                            'relatedLot': lot_id2,
                        },
                    ],
                }
            },
        )
        self.assertEqual(response.status, '201 Created')
        bid2_id = response.json['data']['id']
        bid2_token = response.json['access']['token']
        self.set_responses(tender_id, response.json, "pending")

        response = self.app.patch_json(
            '/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid1_id, bid1_token),
            {
                'data': {
                    'lotValues': [
                        {"subcontractingDetails": "ДКП «Орфей»", "value": {"amount": 500}, 'relatedLot': lot_id1}
                    ],
                    'status': 'pending',
                }
            },
        )
        self.assertEqual(response.status, '200 OK')

        response = self.app.patch_json(
            '/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid2_id, bid2_token),
            {'data': {'lotValues': [{"value": {"amount": 500}, 'relatedLot': lot_id1}], 'status': 'pending'}},
        )
        self.assertEqual(response.status, '200 OK')
        # switch to active.pre-qualification
        self.time_shift('active.pre-qualification')
        self.check_chronograph()
        response = self.app.get('/tenders/{}'.format(tender['id']))

        response = self.app.get('/tenders/{}/qualifications?acc_token={}'.format(self.tender_id, owner_token))
        self.assertEqual(response.content_type, 'application/json')
        qualifications = response.json['data']

        response = self.app.patch_json(
            '/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualifications[0]['id'], owner_token),
            {"data": {'status': 'active', "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active')

        response = self.app.patch_json(
            '/tenders/{}/qualifications/{}?acc_token={}'.format(self.tender_id, qualifications[1]['id'], owner_token),
            {"data": {'status': 'active', "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active')

        self.add_qualification_sign_doc(tender_id, owner_token)
        with open(TARGET_DIR + 'qualification-complain-duration-5-days.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender_id, owner_token),
                {"data": {"status": "active.pre-qualification.stand-still"}},
            )
            self.assertEqual(response.status, "200 OK")
            for qualification in response.json["data"]["qualifications"]:
                end_date = qualification["complaintPeriod"]["endDate"]
                start_date = qualification["complaintPeriod"]["startDate"]
                time_diff = datetime.datetime.fromisoformat(end_date) - datetime.datetime.fromisoformat(start_date)
                self.assertEqual(time_diff.days, 5)


class TenderRestrictedResourceTest(TenderConfigBaseResourceTest):
    initial_auth = ("Basic", ("brokerr", ""))

    def test_docs_restricted_values_csv(self):
        self.write_config_values_csv(
            config_name="restricted",
            file_path=TARGET_CSV_DIR + "restricted-values.csv",
        )

    def test_docs_restricted_tender_mask_mapping_csv(self):
        self.write_config_mask_csv(
            mapping=TENDER_MASK_MAPPING,
            file_path=TARGET_CSV_DIR + "tender-mask-mapping.csv",
        )

    def test_docs_restricted_contract_mask_mapping_csv(self):
        self.write_config_mask_csv(
            mapping=CONTRACT_MASK_MAPPING,
            file_path=TARGET_CSV_DIR + "contract-mask-mapping.csv",
        )

    def create_framework(self):
        data = deepcopy(test_framework_dps_data)
        data["qualificationPeriod"] = {"endDate": (get_now() + datetime.timedelta(days=120)).isoformat()}
        response = self.app.post_json(
            "/frameworks",
            {
                "data": data,
                "config": test_framework_dps_config,
            },
        )
        self.framework_token = response.json["access"]["token"]
        self.framework_id = response.json["data"]["id"]
        return response

    def get_framework(self):
        url = "/frameworks/{}".format(self.framework_id)
        response = self.app.get(url)
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        return response

    def activate_framework(self):
        response = self.app.patch_json(
            "/frameworks/{}?acc_token={}".format(self.framework_id, self.framework_token),
            {"data": {"status": "active"}},
        )
        self.assertEqual(response.status, "200 OK")
        return response

    def create_submission(self):
        data = deepcopy(test_submission_data)
        data["frameworkID"] = self.framework_id
        data["tenderers"][0]["identifier"]["id"] = uuid4().hex
        response = self.app.post_json(
            "/submissions",
            {
                "data": data,
                "config": test_submission_config,
            },
        )
        self.submission_id = response.json["data"]["id"]
        self.submission_token = response.json["access"]["token"]
        return response

    def activate_submission(self):
        response = self.app.patch_json(
            "/submissions/{}?acc_token={}".format(self.submission_id, self.submission_token),
            {"data": {"status": "active"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.qualification_id = response.json["data"]["qualificationID"]
        return response

    def activate_qualification(self):
        response = self.app.post_json(
            "/qualifications/{}/documents?acc_token={}".format(self.qualification_id, self.framework_token),
            {
                "data": {
                    "title": "sign.p7s",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/pkcs7-signature",
                    "documentType": "evaluationReports",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        response = self.app.patch_json(
            f"/qualifications/{self.qualification_id}?acc_token={self.framework_token}",
            {"data": {"status": "active"}},
        )
        self.assertEqual(response.status, "200 OK")
        return response

    def test_docs_restricted(self):
        set_now()
        request_path = '/tenders?opt_pretty=1'

        # Create agreement

        self.tick(datetime.timedelta(days=-15))

        self.create_framework()
        self.activate_framework()

        # TODO: fix tick method
        self.tick(datetime.timedelta(days=30))

        self.create_submission()
        self.activate_submission()
        self.activate_qualification()

        self.create_submission()
        self.activate_submission()
        self.activate_qualification()

        self.create_submission()
        self.activate_submission()
        self.activate_qualification()

        response = self.get_framework()
        self.agreement_id = response.json["data"]["agreementID"]

        # Generate criteria for tenders
        test_criteria_data = deepcopy(test_exclusion_criteria)
        for i in range(len(test_criteria_data)):
            classification_id = test_criteria_data[i]['classification']['id']
            if classification_id == 'CRITERION.EXCLUSION.CONTRIBUTIONS.PAYMENT_OF_TAXES':
                del test_criteria_data[i]
                break
        test_criteria_data.extend(test_language_criteria)
        test_criteria_data.extend(test_contract_guarantee_criteria)

        # Creating tender

        data = deepcopy(test_docs_tender_dps)
        data["items"] = [data["items"][0]]
        data["procurementMethodType"] = "competitiveOrdering"
        data['procuringEntity']['identifier']['id'] = test_framework_dps_data['procuringEntity']['identifier']['id']

        data['agreements'] = [{'id': self.agreement_id}]

        lot = deepcopy(test_docs_lots[0])
        lot['value'] = data['value']
        lot['minimalStep'] = data['minimalStep']
        lot['id'] = uuid4().hex

        data['lots'] = [lot]

        config = deepcopy(test_tender_dps_config)

        for item in data['items']:
            item['relatedLot'] = lot['id']
            item['deliveryDate'] = {
                "startDate": (get_now() + datetime.timedelta(days=2)).isoformat(),
                "endDate": (get_now() + datetime.timedelta(days=5)).isoformat(),
            }
            item['classification']['id'] = test_framework_dps_data['classification']['id']
        for milestone in data["milestones"]:
            milestone["relatedLot"] = lot["id"]

        # Create not masked tender
        with open(TARGET_DIR + 'restricted-false-tender-post.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders?opt_pretty=1', {'data': data, 'config': config})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = tender["lots"][0]["id"]
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token), {"data": {"items": items}}
        )
        self.assertEqual(response.status, '200 OK')

        # add criteria
        response = self.app.post_json(
            '/tenders/{}/criteria?acc_token={}'.format(tender_id, owner_token), {'data': test_criteria_data}
        )
        self.assertEqual(response.status, '201 Created')

        # Tender activating
        self.add_notice_doc(tender_id, owner_token)
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token), {'data': {"status": "active.tendering"}}
        )
        self.assertEqual(response.status, '200 OK')

        # Get not masked tender
        with change_auth(self.app, None):
            with open(TARGET_DIR + 'restricted-false-tender-get-anon.http', 'w') as self.app.file_obj:
                response = self.app.get('/tenders/{}'.format(tender_id))
                self.assertEqual(response.status, '200 OK')

        assert response.json["data"]["procuringEntity"]["name"] != MASK_STRING

        # Create masked tender
        agreement_doc = self.mongodb.agreements.get(self.agreement_id)
        agreement_doc["config"]["restricted"] = True
        self.mongodb.agreements.save(agreement_doc)

        config["restricted"] = True

        with open(TARGET_DIR + 'restricted-true-tender-post.http', 'w') as self.app.file_obj:
            response = self.app.post_json('/tenders?opt_pretty=1', {'data': data, 'config': config})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = tender["lots"][0]["id"]
        with open(TARGET_DIR + 'tender-add-relatedLot-to-item.http', 'w') as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}?acc_token={}'.format(tender_id, owner_token), {"data": {"items": items}}
            )
            self.assertEqual(response.status, '200 OK')

        # add criteria

        response = self.app.post_json(
            '/tenders/{}/criteria?acc_token={}'.format(tender_id, owner_token), {'data': test_criteria_data}
        )
        self.assertEqual(response.status, '201 Created')

        # Tender activating
        self.add_notice_doc(tender_id, owner_token)
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token), {'data': {"status": "active.tendering"}}
        )
        self.assertEqual(response.status, '200 OK')

        response = self.app.post_json(
            '/tenders/{}/documents?acc_token={}'.format(tender_id, owner_token),
            {
                "data": {
                    "title": "sign.p7s",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/pdf",
                }
            },
        )
        self.assertEqual(response.status, '201 Created')

        response = self.app.post_json(
            '/tenders/{}/documents?acc_token={}'.format(tender_id, owner_token),
            {
                "data": {
                    "title": "description.pdf",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/pdf",
                }
            },
        )
        self.assertEqual(response.status, '201 Created')

        # Get masked tender by anon (should be masked)
        with change_auth(self.app, None):
            with open(TARGET_DIR + 'restricted-true-tender-get-anon.http', 'w') as self.app.file_obj:
                response = self.app.get('/tenders/{}'.format(tender_id))
                self.assertEqual(response.status, '200 OK')

        assert response.json["data"]["items"][0]["deliveryAddress"]["streetAddress"] == MASK_STRING

        # Get not masked tender by broker (should not be masked)
        with open(TARGET_DIR + 'restricted-true-tender-get.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders/{}'.format(tender_id))
            self.assertEqual(response.status, '200 OK')

        assert response.json["data"]["procuringEntity"]["name"] != MASK_STRING

        # Get feed by anon
        with change_auth(self.app, None):
            with open(TARGET_DIR + 'restricted-tender-feed-anon.http', 'w') as self.app.file_obj:
                response = self.app.get('/tenders?opt_fields=procuringEntity')
                self.assertEqual(response.status, '200 OK')

        # Get feed by broker
        with open(TARGET_DIR + 'restricted-tender-feed.http', 'w') as self.app.file_obj:
            response = self.app.get('/tenders?opt_fields=procuringEntity')
            self.assertEqual(response.status, '200 OK')

        # Create contract
        data = deepcopy(test_contract_data)
        data.update(
            {
                "dateSigned": get_now().isoformat(),
                "id": uuid4().hex,
                "tender_id": tender_id,
                "tender_token": sha512(uuid4().hex.encode()).hexdigest(),
            }
        )

        with change_auth(self.app, ('Basic', ('contracting', ''))):
            response = self.app.post_json('/contracts', {'data': data})
        self.assertEqual(response.status, '201 Created')
        contract = response.json['data']
        contract_id = contract['id']

        with change_auth(self.app, None):
            with open(TARGET_DIR + 'restricted-true-contract-get-anon.http', 'w') as self.app.file_obj:
                response = self.app.get('/contracts/{}'.format(contract_id))
                self.assertEqual(response.status, '200 OK')

        with open(TARGET_DIR + 'restricted-true-contract-get.http', 'w') as self.app.file_obj:
            response = self.app.get('/contracts/{}'.format(contract_id))
            self.assertEqual(response.status, '200 OK')


class TenderAwardComplainDurationResourceTest(TenderConfigBaseResourceTest):
    initial_data = deepcopy(test_docs_tender_below)

    def test_docs_award_complain_duration_values_csv(self):
        self.write_config_values_csv(
            config_name="awardComplainDuration",
            file_path=TARGET_CSV_DIR + "award-complain-duration-values.csv",
        )

    def test_docs_award_complain_duration_complaint_period_exists(self):
        config = deepcopy(self.initial_config)
        config["hasAwardingOrder"] = False

        test_tender_data = deepcopy(test_docs_tender_below)
        test_lots = deepcopy(test_docs_lots[:1])
        test_lots[0]['value'] = test_tender_data['value']
        test_lots[0]['minimalStep'] = test_tender_data['minimalStep']
        set_tender_lots(test_tender_data, test_lots)

        # Creating tender
        with open(TARGET_DIR + "award-complain-duration-tender-post-1.http", "w") as self.app.file_obj:
            response = self.app.post_json('/tenders?opt_pretty=1', {'data': test_tender_data, 'config': config})
            self.assertEqual(response.status, '201 Created')

        tender = response.json['data']
        tender_id = self.tender_id = tender['id']
        owner_token = response.json['access']['token']
        lots = response.json['data']["lots"]
        lot_id = lots[0]["id"]

        self.app.authorization = ('Basic', ('broker', ''))
        self.add_criteria(tender_id, owner_token)

        # Tender activating
        self.add_notice_doc(tender_id, owner_token)
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender_id, owner_token), {'data': {"status": "active.enquiries"}}
        )
        self.assertEqual(response.status, '200 OK')

        # enquires
        response = self.app.post_json(
            '/tenders/{}/questions'.format(tender_id), {"data": test_docs_question}, status=201
        )
        question_id = response.json['data']['id']
        self.assertEqual(response.status, '201 Created')

        response = self.app.patch_json(
            '/tenders/{}/questions/{}?acc_token={}'.format(tender_id, question_id, owner_token),
            {"data": {"answer": "Таблицю додано в файлі \"Kalorijnist.xslx\""}},
            status=200,
        )
        self.assertEqual(response.status, '200 OK')
        self.set_status('active.tendering')

        # register bids
        bids = []
        bids_tokens = []
        for idx in range(3):
            self.app.authorization = ('Basic', ('broker', ''))
            bid_data = {'status': 'draft', 'tenderers': test_docs_bid["tenderers"], "value": {"amount": 500 - idx}}
            set_bid_lotvalues(bid_data, lots)
            response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bid_data})
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
            'bids': [
                {"id": bids[0], "lotValues": [{"participationUrl": '{}?key_for_bid={}'.format(auction_url, bids[0])}]},
                {
                    "id": bids[1],
                    "lotValues": [
                        {"participationUrl": '{}?key_for_bid={}'.format(auction_url, bids[1])},
                    ],
                },
                {
                    "id": bids[2],
                    "lotValues": [
                        {"participationUrl": '{}?key_for_bid={}'.format(auction_url, bids[2])},
                    ],
                },
            ],
        }
        response = self.app.patch_json(
            '/tenders/{}/auction/{}?acc_token={}'.format(self.tender_id, lot_id, owner_token), {'data': patch_data}
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
                                {"value": lot["value"], "relatedLot": lot["relatedLot"]} for lot in b["lotValues"]
                            ],
                        }
                        for b in auction_bids_data
                    ]
                }
            },
        )
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        award_1_id = response.json["data"]["awards"][0]["id"]

        self.app.authorization = ('Basic', ('broker', ''))
        # The customer decides that the winner is award1
        with open(TARGET_DIR + "award-complain-duration-tender-patch-1.http", "w") as self.app.file_obj:
            # set award as active
            response = self.app.patch_json(
                '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, award_1_id, owner_token),
                {'data': {'status': 'active'}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertIn("complaintPeriod", response.json["data"])


class TenderCancellationComplainDurationResourceTest(TenderConfigBaseResourceTest):
    initial_data = deepcopy(test_docs_tender_below)

    def test_docs_cancellation_complain_duration_values_csv(self):
        self.write_config_values_csv(
            config_name="cancellationComplainDuration",
            file_path=TARGET_CSV_DIR + "cancellation-complain-duration-values.csv",
        )

    def test_docs_cancellation_complain_duration_complaint_period_exists(self):
        config = deepcopy(test_tender_open_config)
        test_tender_data = deepcopy(test_docs_tender_open)

        # Create tender
        with open(TARGET_DIR + "cancellation-complain-duration-tender-post-1.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders?opt_pretty=1",
                {"data": test_tender_data, "config": config},
            )
            self.assertEqual(response.status, "201 Created")

        tender = response.json["data"]
        tender_id = self.tender_id = tender["id"]
        owner_token = response.json["access"]["token"]

        self.app.authorization = ("Basic", ("broker", ""))

        # add lot
        test_lot = deepcopy(test_docs_lots[0])
        test_lot["value"] = test_tender_data["value"]
        test_lot["minimalStep"] = test_tender_data["minimalStep"]
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token),
            {"data": test_lot},
        )
        self.assertEqual(response.status, "201 Created")
        lot = response.json["data"]
        lot_id = lot["id"]

        # add relatedLot for item
        items = deepcopy(tender["items"])
        for item in items:
            item["relatedLot"] = lot_id
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender["id"], owner_token), {"data": {"items": items}}
        )
        self.assertEqual(response.status, '200 OK')

        self.set_status("active.tendering")

        response = self.app.post_json(
            '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, owner_token),
            {'data': {'reason': 'cancellation reason', 'reasonType': 'noDemand'}},
        )
        cancellation_id = response.json['data']['id']
        self.assertEqual(response.status, '201 Created')

        response = self.app.post_json(
            '/tenders/{}/cancellations/{}/documents?acc_token={}'.format(self.tender_id, cancellation_id, owner_token),
            {
                "data": {
                    "title": "Notice.pdf",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/pdf",
                }
            },
        )
        self.assertEqual(response.status, '201 Created')

        with open(TARGET_DIR + "cancellation-complain-duration-tender-patch-1.http", "w") as self.app.file_obj:

            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation_id, owner_token),
                {'data': {"status": "pending"}},
            )
            self.assertEqual(response.status, '200 OK')
            self.assertIn("complaintPeriod", response.json["data"])

    def test_docs_cancellation_complain_duration_complaint_period_dont_exist(self):
        config = deepcopy(self.initial_config)

        # Create tender
        with open(TARGET_DIR + "cancellation-complain-duration-tender-post-2.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders?opt_pretty=1",
                {"data": self.initial_data, "config": config},
            )
            self.assertEqual(response.status, "201 Created")

        tender = response.json["data"]
        tender_id = self.tender_id = tender["id"]
        owner_token = response.json["access"]["token"]

        self.app.authorization = ("Basic", ("broker", ""))

        # add lot
        test_lot = deepcopy(test_docs_lots[0])
        test_lot["value"] = self.initial_data["value"]
        test_lot["minimalStep"] = self.initial_data["minimalStep"]
        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token),
            {"data": test_lot},
        )
        self.assertEqual(response.status, "201 Created")
        lot = response.json["data"]
        lot_id = lot["id"]

        # add relatedLot for item
        items = deepcopy(tender["items"])
        for item in items:
            item["relatedLot"] = lot_id
        response = self.app.patch_json(
            '/tenders/{}?acc_token={}'.format(tender["id"], owner_token), {"data": {"items": items}}
        )
        self.assertEqual(response.status, '200 OK')

        self.set_status("active.tendering")

        response = self.app.post_json(
            '/tenders/{}/cancellations?acc_token={}'.format(self.tender_id, owner_token),
            {'data': {'reason': 'cancellation reason', 'reasonType': 'noDemand'}},
        )
        cancellation_id = response.json['data']['id']
        self.assertEqual(response.status, '201 Created')

        response = self.app.post_json(
            '/tenders/{}/cancellations/{}/documents?acc_token={}'.format(self.tender_id, cancellation_id, owner_token),
            {
                "data": {
                    "title": "Notice.pdf",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/pdf",
                }
            },
        )
        with open(TARGET_DIR + "cancellation-complain-duration-tender-patch-2.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                '/tenders/{}/cancellations/{}?acc_token={}'.format(self.tender_id, cancellation_id, owner_token),
                {'data': {"status": "pending"}},
            )
            self.assertEqual(response.status, '200 OK')
            self.assertNotIn("complaintPeriod", response.json["data"])


class CancellationComplainDurationResourceTest(TenderConfigBaseResourceTest):
    initial_data = deepcopy(test_docs_tender_below)

    def test_docs_cancellation_complain_duration_values_csv(self):
        self.write_config_values_csv(
            config_name="cancellationComplainDuration",
            file_path=TARGET_CSV_DIR + "cancellation-complain-duration-values.csv",
        )

    def activate_tender(self, tender_id, owner_token):
        #### Tender activating
        self.add_notice_doc(tender_id, owner_token)
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(tender_id, owner_token),
            {"data": {"status": "active.tendering"}},
        )
        self.assertEqual(response.status, "200 OK")

    def activate_tender_enquiries(self, tender_id, owner_token):
        #### Tender activating
        self.add_notice_doc(tender_id, owner_token)
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(tender_id, owner_token),
            {"data": {"status": "active.enquiries"}},
        )
        self.assertEqual(response.status, "200 OK")

        # enquires
        response = self.app.post_json(
            "/tenders/{}/questions".format(tender_id),
            {"data": test_docs_question},
            status=201,
        )
        question_id = response.json["data"]["id"]
        self.assertEqual(response.status, "201 Created")

        response = self.app.patch_json(
            "/tenders/{}/questions/{}?acc_token={}".format(tender_id, question_id, owner_token),
            {"data": {"answer": 'Таблицю додано в файлі "Kalorijnist.xslx"'}},
            status=200,
        )
        self.assertEqual(response.status, "200 OK")
        self.set_status("active.tendering")

    def test_docs_cancellation_complain_duration_complaint_period_exists(self):
        config = deepcopy(test_tender_open_config)
        test_tender_data = deepcopy(test_docs_tender_open)

        # Create tender
        with open(TARGET_DIR + "cancellation-complain-duration-tender-post-1.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders?opt_pretty=1",
                {"data": test_tender_data, "config": config},
            )
            self.assertEqual(response.status, "201 Created")

        tender = response.json["data"]
        tender_id = self.tender_id = tender["id"]
        owner_token = response.json["access"]["token"]

        self.app.authorization = ("Basic", ("broker", ""))

        # add lots
        test_lots = deepcopy(test_docs_lots)
        test_lots[0]["value"] = test_tender_data["value"]
        test_lots[0]["minimalStep"] = test_tender_data["minimalStep"]
        test_lots[1]["value"] = test_tender_data["value"]
        test_lots[1]["minimalStep"] = test_tender_data["minimalStep"]

        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token),
            {"data": test_lots[0]},
        )
        self.assertEqual(response.status, "201 Created")
        lot_id1 = response.json["data"]["id"]

        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token),
            {"data": test_lots[1]},
        )
        self.assertEqual(response.status, "201 Created")
        lot_id2 = response.json["data"]["id"]

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = lot_id1
        items[1]["relatedLot"] = lot_id2

        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(tender_id, owner_token),
            {"data": {"items": items}},
        )
        self.assertEqual(response.status, "200 OK")

        # add cancellation for item
        self.add_criteria(tender_id, owner_token)
        self.activate_tender(tender_id, owner_token)

        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, owner_token),
            {"data": {"reason": "cancellation reason", "reasonType": "unFixable"}},
        )
        self.assertEqual(response.status, "201 Created")
        cancellation_id = response.json["data"]["id"]

        # add cancellation document
        response = self.app.post_json(
            '/tenders/{}/cancellations/{}/documents?acc_token={}'.format(self.tender_id, cancellation_id, owner_token),
            {
                "data": {
                    "title": "Notice.pdf",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/pdf",
                }
            },
        )
        self.assertEqual(response.status, '201 Created')
        with open(TARGET_DIR + "cancellation-complain-duration-tender-patch-1.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, owner_token),
                {"data": {"status": "pending"}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertIn("complaintPeriod", response.json["data"])

    def test_docs_cancellation_complain_duration_complaint_period_dont_exist(self):
        config = deepcopy(self.initial_config)
        test_tender_data = deepcopy(self.initial_data)

        # Create tender
        with open(TARGET_DIR + "cancellation-complain-duration-tender-post-2.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                "/tenders?opt_pretty=1",
                {"data": self.initial_data, "config": config},
            )
            self.assertEqual(response.status, "201 Created")

        tender = response.json["data"]
        tender_id = self.tender_id = tender["id"]
        owner_token = response.json["access"]["token"]

        self.app.authorization = ("Basic", ("broker", ""))

        # add lots
        test_lots = deepcopy(test_docs_lots)
        test_lots[0]["value"] = test_tender_data["value"]
        test_lots[0]["minimalStep"] = test_tender_data["minimalStep"]
        test_lots[1]["value"] = test_tender_data["value"]
        test_lots[1]["minimalStep"] = test_tender_data["minimalStep"]

        response = self.app.post_json(
            "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token),
            {"data": test_lots[0]},
        )
        self.assertEqual(response.status, "201 Created")
        lot_id1 = response.json["data"]["id"]

        # add relatedLot for item
        items = deepcopy(tender["items"])
        items[0]["relatedLot"] = lot_id1

        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(tender_id, owner_token),
            {"data": {"items": items}},
        )
        self.assertEqual(response.status, "200 OK")

        # add cancellation for item
        self.add_criteria(tender_id, owner_token)
        self.activate_tender_enquiries(tender_id, owner_token)

        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, owner_token),
            {"data": {"reason": "cancellation reason", "reasonType": "unFixable"}},
        )
        self.assertEqual(response.status, "201 Created")
        cancellation_id = response.json["data"]["id"]

        # add cancellation document
        response = self.app.post_json(
            '/tenders/{}/cancellations/{}/documents?acc_token={}'.format(self.tender_id, cancellation_id, owner_token),
            {
                "data": {
                    "title": "Notice.pdf",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/pdf",
                }
            },
        )
        self.assertEqual(response.status, '201 Created')
        with open(TARGET_DIR + "cancellation-complain-duration-tender-patch-1.http", "w") as self.app.file_obj:
            response = self.app.patch_json(
                "/tenders/{}/cancellations/{}?acc_token={}".format(self.tender_id, cancellation_id, owner_token),
                {"data": {"status": "pending"}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertNotIn("complaintPeriod", response.json["data"])


class TenderClarificationUntilDurationResourceTest(TenderConfigBaseResourceTest):

    def test_docs_clarification_until_duration_values_csv(self):
        self.write_config_values_csv(
            config_name="clarificationUntilDuration",
            file_path=TARGET_CSV_DIR + "clarification-until-duration-values.csv",
        )

    def test_clarification_until_duration_one_working_day(self):
        with open(TARGET_DIR + "clarification-until-duration-1-working-day.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': deepcopy(test_docs_tender_below_maximum), 'config': deepcopy(test_tender_below_config)},
            )
            self.assertEqual(response.status, '201 Created')
            end_date = dt_from_iso(response.json["data"]['enquiryPeriod']['endDate'])
            expected_clarif_until = calculate_clarif_business_date(
                end_date,
                datetime.timedelta(days=test_tender_below_config["clarificationUntilDuration"]),
                response.json["data"],
                True,
            )
            self.assertEqual(
                expected_clarif_until.isoformat(), response.json["data"]["enquiryPeriod"]["clarificationsUntil"]
            )

    def test_clarification_until_duration_three_calendar_days(self):
        with open(TARGET_DIR + "clarification-until-duration-3-calendar-days.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': deepcopy(test_docs_tender_open), 'config': deepcopy(test_tender_open_config)},
            )
            self.assertEqual(response.status, '201 Created')
            end_date = dt_from_iso(response.json["data"]['enquiryPeriod']['endDate'])
            expected_clarif_until = calculate_clarif_business_date(
                end_date,
                datetime.timedelta(days=test_tender_open_config["clarificationUntilDuration"]),
                response.json["data"],
                False,
            )
            self.assertEqual(
                expected_clarif_until.isoformat(), response.json["data"]["enquiryPeriod"]["clarificationsUntil"]
            )

    def test_clarification_until_duration_three_working_days(self):
        with open(TARGET_DIR + "clarification-until-duration-3-working-days.http", "w") as self.app.file_obj:
            response = self.app.post_json(
                '/tenders?opt_pretty=1',
                {'data': deepcopy(test_docs_tender_esco), 'config': deepcopy(test_tender_esco_config)},
            )
            self.assertEqual(response.status, '201 Created')
            end_date = dt_from_iso(response.json["data"]['enquiryPeriod']['endDate'])
            expected_clarif_until = calculate_clarif_business_date(
                end_date,
                datetime.timedelta(days=test_tender_openeu_config["clarificationUntilDuration"]),
                response.json["data"],
                True,
            )
            self.assertEqual(
                expected_clarif_until.isoformat(), response.json["data"]["enquiryPeriod"]["clarificationsUntil"]
            )
