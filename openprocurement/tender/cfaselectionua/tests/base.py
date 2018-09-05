# -*- coding: utf-8 -*-
import json
import os
from copy import deepcopy
from datetime import datetime, timedelta
from uuid import uuid4

from openprocurement.api.constants import SANDBOX_MODE, TZ
from openprocurement.api.utils import apply_data_patch
from openprocurement.tender.core.tests.base import (
    BaseTenderWebTest as BaseTWT
)
from openprocurement.tender.cfaselectionua.constants import DRAFT_FIELDS, BOT_NAME, ENQUIRY_PERIOD
from openprocurement.tender.cfaselectionua.tests.periods import get_periods


here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, 'data/agreement.json')) as _in:
    test_agreement = json.load(_in)

now = datetime.now(TZ)
test_organization = {
    "name": u"Державне управління справами",
    "identifier": {
        "scheme": u"UA-EDR",
        "id": u"00037256",
        "uri": u"http://www.dus.gov.ua/"
    },
    "address": {
        "countryName": u"Україна",
        "postalCode": u"01220",
        "region": u"м. Київ",
        "locality": u"м. Київ",
        "streetAddress": u"вул. Банкова, 11, корпус 1"
    },
    "contactPoint": {
        "name": u"Державне управління справами",
        "telephone": u"0440000000"
    }
}
test_procuringEntity = test_organization.copy()
test_procuringEntity["kind"] = "general"

test_items = [
    {
        "id": test_agreement['items'][0]['id'],
        "description": u"футляри до державних нагород",
        "classification": {
            "scheme": u"ДК021",
            "id": u"44617100-9",
            "description": u"Cartons"
        },
        "additionalClassifications": [
            {
                "scheme": u"ДКПП",
                "id": u"17.21.1",
                "description": u"папір і картон гофровані, паперова й картонна тара"
            }
        ],
        "unit": {
            "name": u"item",
            "code": u"44617100-9"
        },
        "quantity": 5,
        "deliveryDate": {
            "startDate": (now + timedelta(days=2)).isoformat(),
            "endDate": (now + timedelta(days=5)).isoformat()
        },
        "deliveryAddress": {
            "countryName": u"Україна",
            "postalCode": "79000",
            "region": u"м. Київ",
            "locality": u"м. Київ",
            "streetAddress": u"вул. Банкова 1"
        }
    }
]
test_tender_data = {
    "agreements": [{"id": "1" * 32}],
    "title": u"футляри до державних нагород",
    "procuringEntity": test_procuringEntity,
    "value": {
        "amount": 500,
        "currency": u"UAH"
    },
    "minimalStep": {
        "amount": 35,
        "currency": u"UAH"
    },
    "enquiryPeriod": {
        "endDate": (now + ENQUIRY_PERIOD).isoformat()
    },
    "tenderPeriod": {
        "endDate": (now + timedelta(days=14)).isoformat()
    },
    "procurementMethodType": "closeFrameworkAgreementSelectionUA",
    "items": test_items
}
if SANDBOX_MODE:
    test_tender_data['procurementMethodDetails'] = 'quick, accelerator=1440'
test_features_tender_data = test_tender_data.copy()
test_features_item = test_items[0].copy()
# test_features_item['id'] = "1"
test_features_tender_data['items'] = [test_features_item]
test_features_tender_data["features"] = [
    {
        "code": "OCDS-123454-AIR-INTAKE",
        "featureOf": "item",
        "relatedItem": test_agreement['items'][0]['id'],
        "title": u"Потужність всмоктування",
        "title_en": "Air Intake",
        "description": u"Ефективна потужність всмоктування пилососа, в ватах (аероватах)",
        "enum": [
            {
                "value": 0.1,
                "title": u"До 1000 Вт"
            },
            {
                "value": 0.15,
                "title": u"Більше 1000 Вт"
            }
        ]
    },
    {
        "code": "OCDS-123454-YEARS",
        "featureOf": "tenderer",
        "title": u"Років на ринку",
        "title_en": "Years trading",
        "description": u"Кількість років, які організація учасник працює на ринку",
        "enum": [
            {
                "value": 0.05,
                "title": u"До 3 років"
            },
            {
                "value": 0.1,
                "title": u"Більше 3 років, менше 5 років"
            },
            {
                "value": 0.15,
                "title": u"Більше 5 років"
            }
        ]
    }
]
test_bids = [
    {
        "tenderers": [
            test_organization
        ],
        "value": {
            "amount": 469,
            "currency": "UAH",
            "valueAddedTaxIncluded": True
        }
    },
    {
        "tenderers": [
            test_organization
        ],
        "value": {
            "amount": 479,
            "currency": "UAH",
            "valueAddedTaxIncluded": True
        }
    }
]
test_lots = [
    {
        'title': 'lot title',
        'description': 'lot description',
        'value': test_tender_data['value'],
        'minimalStep': test_tender_data['minimalStep'],
    }
]
test_lots[0]['value']['amount'] += 100
test_features = [
    {
        "code": "OCDS-123454-AIR-INTAKE",
        "featureOf": "item",
        "relatedItem": test_agreement['items'][0]['id'],
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
        "code": "OCDS-123454-YEARS",
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
test_agreement['features'] = test_features


class BaseTenderWebTest(BaseTWT):
    initial_data = test_tender_data
    initial_status = None
    initial_bids = None
    initial_lots = None
    initial_auth = ('Basic', ('broker', ''))
    docservice = False
    relative_to = os.path.dirname(__file__)
    # Statuses for test, that will be imported from others procedures
    primary_tender_status = 'draft.pending'  # status, to which tender should be switched from 'draft'
    forbidden_document_modification_actions_status = 'active.tendering'  # status, in which operations with tender documents (adding, updating) are forbidden
    forbidden_question_modification_actions_status = 'active.tendering'  # status, in which adding/updating tender questions is forbidden
    forbidden_lot_actions_status = 'active.tendering'  # status, in which operations with tender lots (adding, updating, deleting) are forbidden
    forbidden_contract_document_modification_actions_status = 'unsuccessful'  # status, in which operations with tender's contract documents (adding, updating) are forbidden
    # auction role actions
    forbidden_auction_actions_status = 'active.tendering'  # status, in which operations with tender auction (getting auction info, reporting auction results, updating auction urls) and adding tender documents are forbidden
    forbidden_auction_document_create_actions_status = 'active.tendering'  # status, in which adding document to tender auction is forbidden

    meta_initial_bids = test_bids
    meta_initial_lots = test_lots
    periods = get_periods()

    def calculate_agreement_contracts_value_amount(self, agreement, items):
        for contract in agreement['contracts']:
            value = deepcopy(contract['unitPrices'][0]['value'])
            value['amount'] = 0
            for unitPrice in contract['unitPrices']:
                quantity = [i for i in items if i['id'] == unitPrice['relatedItem']][0]['quantity']
                value['amount'] += unitPrice['value']['amount'] * quantity
            contract['value'] = value

    def patch_agreements_by_bot(self, status, start_end='start'):
        self.tender_patch.update(self.periods[status][start_end])
        agreements = self.tender_document.get('agreements', [])
        for agreement in agreements:
            agreement.update(test_agreement)
            items = self.tender_document.get('items')
            if items:
                self.calculate_agreement_contracts_value_amount(agreement, items)
        self.tender_patch.update({'agreements': agreements})

    def generate_bids(self, status, start_end='start'):
        self.tender_patch.update(self.periods[status][start_end])
        bids = self.tender_document.get('bids', [])

        if not bids and self.initial_bids:
            self.tender_patch['bids'] = []
            self.initial_bids_tokens = {}
            for bid in self.initial_bids:
                bid = bid.copy()
                value = bid.pop('value')
                bid.update({
                    'id': uuid4().hex,
                    'owner_token': uuid4().hex,
                    'owner': 'broker',
                    'status': 'active'
                })
                if self.initial_lots:
                    bid.update({
                        'lotValues': [
                            {
                                'value': value,
                                'relatedLot': l['id'],
                            }
                            for l in self.initial_lots
                        ]
                    })
                self.tender_patch['bids'].append(bid)
            self.initial_bids = self.tender_patch['bids']
            bids = self.initial_bids
        if bids:
            self.bid_id = bids[0]['id']
            self.bid_token = bids[0]['owner_token']

    def prepare_for_auction(self, status, start_end='start'):
        self.tender_patch.update(self.periods[status][start_end])
        if self.initial_lots:
            self.tender_patch.update({
                'lots': [
                    {
                        "auctionPeriod": {
                            "startDate": datetime.now(TZ).isoformat()
                        }
                    }
                    for i in self.initial_lots
                ]
            })

    def generate_awards(self, status, start_end='start'):
        self.tender_patch.update(self.periods[status][start_end])
        if self.initial_lots:
            self.tender_patch.update({
                'lots': [
                    {
                        "auctionPeriod": {
                            "startDate": (datetime.now(TZ) - timedelta(days=1)).isoformat(),
                            "endDate": datetime.now(TZ).isoformat()
                        }
                    }
                    for i in self.initial_lots
                ]
            })
        bids = self.tender_document.get('bids', []) or self.tender_patch.get('bids', [])
        lots = self.tender_document.get('lots', []) or self.tender_patch.get('lots', [])
        if 'awards' not in self.tender_document:
            self.tender_patch['awards'] = []
            if lots:
                active_lots = {lot['id']: 0 for lot in lots if lot['status'] == 'active'}
                self.tender_patch['awards'] = []
                for bid in bids[:1]:
                    for lot_value in bid['lotValues']:
                        if lot_value['relatedLot'] in active_lots:
                            award = {
                                'status': 'pending',
                                'lotID': lot_value['relatedLot'],
                                'suppliers': bid['tenderers'],
                                'bid_id': bid['id'],
                                'value': lot_value['value'],
                                'date': datetime.now(TZ).isoformat(),
                                'id': uuid4().hex
                            }
                            self.tender_patch['awards'].append(award)
                            self.award = award
                            self.award_id = award['id']
                            active_lots[lot_value['relatedLot']] += 1
            else:
                for bid in bids[:1]:
                    award = {
                        'status': 'pending',
                        'suppliers': bid['tenderers'],
                        'bid_id': bid['id'],
                        'value': bid['value'],
                        'date': datetime.now(TZ).isoformat(),
                        'id': uuid4().hex
                    }
                    self.award = award
                    self.award_id = award['id']
                    self.tender_patch['awards'].append(award)

    def activate_awards_and_generate_contract(self, status, start_end='start'):
        self.tender_patch.update(self.periods[status][start_end])
        awards = self.tender_document.get('awards', [])
        if not awards:
            awards = self.tender_patch.get('awards', [])
        for award in awards:
            if award['status'] == 'pending':
                award.update({'status': 'active'})
        self.tender_patch.update({'awards': awards})
        contracts = self.tender_document.get('contracts', [])

        if not contracts:
            for award in awards:
                if award['status'] == 'active':
                    contract = {
                        'id': uuid4().hex,
                        'title': 'contract title',
                        'description': 'contract description',
                        'awardID': award['id'],
                        'value': award['value'],
                        'suppliers': award['suppliers'],
                        'status': 'pending',
                        'contractID': 'UA-2017-06-21-000001-1',
                        'date': datetime.now(TZ).isoformat(),
                        'items': [i for i in self.tender_document['items'] if i['relatedLot'] == award['lotID']],
                    }
                    self.contract_id = contract['id']
                    self.tender_patch.update({'contracts': [contract]})

    def complete_tender(self, status, start_end='start'):
        self.tender_patch.update(self.periods[status][start_end])
        if self.initial_lots:
            self.tender_patch.update({
                'lots': [
                    {
                        "auctionPeriod": {
                            "startDate": (datetime.now(TZ) - timedelta(days=11)).isoformat(),
                            "endDate": (datetime.now(TZ) - timedelta(days=10)).isoformat()
                        }
                    }
                    for i in self.initial_lots
                ]
            })

    def create_tender(self):
        data = deepcopy(self.initial_data)
        if self.initial_lots:
            lots = []
            for i in self.initial_lots:
                lot = deepcopy(i)
                lot['id'] = uuid4().hex
                lots.append(lot)
            data['lots'] = self.initial_lots = lots
            for i, item in enumerate(data['items']):
                item['relatedLot'] = lots[i % len(lots)]['id']
        response = self.app.post_json('/tenders', {'data': data})
        tender = response.json['data']
        self.tender_token = response.json['access']['token']
        self.tender_id = tender['id']
        status = tender['status']
        if self.initial_status != status and self.initial_status:
            self.set_status(self.initial_status)

    def get_tender(self, role):
        authorization = self.app.authorization
        self.app.authorization = ('Basic', (role, ''))

        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.app.authorization = authorization
        self.assertEqual((response.status, response.content_type), ('200 OK', 'application/json'))
        return response

    def set_status(self, status, extra=None, start_end='start'):

        self.tender_document = self.db.get(self.tender_id)
        self.tender_patch = {'status': status}
        self.periods = get_periods()

        if status == 'active.enquiries':
            self.patch_agreements_by_bot(status, start_end)
        elif status == 'active.tendering':
            self.patch_agreements_by_bot(status, start_end)
            self.generate_bids(status, start_end)
        elif status == 'active.auction':
            self.patch_agreements_by_bot(status, start_end)
            self.generate_bids(status, start_end)
            self.prepare_for_auction(status, start_end)
        elif status == 'active.qualification':
            self.patch_agreements_by_bot(status, start_end)
            self.generate_bids(status, start_end)
            self.prepare_for_auction(status, start_end)
            self.generate_awards(status, start_end)
        elif status == 'active.awarded':
            self.patch_agreements_by_bot(status, start_end)
            self.generate_bids(status, start_end)
            self.prepare_for_auction(status, start_end)
            self.generate_awards(status, start_end)
            self.activate_awards_and_generate_contract(status, start_end)
        elif status == 'complete':
            self.patch_agreements_by_bot(status, start_end)
            self.generate_bids(status, start_end)
            self.prepare_for_auction(status, start_end)
            self.generate_awards(status, start_end)
            self.activate_awards_and_generate_contract(status, start_end)
            self.complete_tender(status, start_end)

        if extra:
            self.tender_patch.update(extra)

        self.save_changes()
        return self.get_tender('chronograph')

    def save_changes(self):
        for period in ('auctionPeriod', 'awardPeriod'):
            self.tender_document.pop(period, None)  # delete all old periods
        self.tender_document.update(apply_data_patch(self.tender_document, self.tender_patch))
        self.db.save(self.tender_document)


class TenderContentWebTest(BaseTenderWebTest):
    initial_data = test_tender_data
    initial_status = None
    initial_bids = None
    initial_lots = None

    def setUp(self):
        super(TenderContentWebTest, self).setUp()
        self.create_tender()
