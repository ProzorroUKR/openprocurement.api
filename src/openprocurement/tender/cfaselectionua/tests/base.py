# -*- coding: utf-8 -*-
import json
import os
from copy import deepcopy
from datetime import datetime, timedelta
from uuid import uuid4

from openprocurement.api.constants import SANDBOX_MODE, TZ
from openprocurement.api.utils import apply_data_patch, get_now
from openprocurement.tender.core.tests.base import (
    BaseTenderWebTest as BaseTWT
)
from openprocurement.tender.cfaselectionua.adapters.configurator import TenderCfaSelectionUAConfigurator
from openprocurement.tender.cfaselectionua.constants import ENQUIRY_PERIOD
from openprocurement.tender.cfaselectionua.tests.periods import periods


here = os.path.dirname(os.path.abspath(__file__))
now = datetime.now(TZ)

with open(os.path.join(here, 'data/agreement.json')) as _in:
    test_agreement = json.load(_in)

with open(os.path.join(here, 'data/organization.json')) as _in:
    test_organization = json.load(_in)

with open(os.path.join(here, 'data/features.json')) as _in:
    test_features = json.load(_in)

test_features[0]['relatedItem'] = test_agreement['items'][0]['id']

with open(os.path.join(here, 'data/items.json')) as _in:
    test_items = json.load(_in)

with open(os.path.join(here, 'data/bids.json')) as _in:
    test_bids = json.load(_in)


with open(os.path.join(here, 'data/procuringEntity.json')) as _in:
    test_procuringEntity = json.load(_in)

test_items[0]['id'] = test_agreement['items'][0]['id']
test_items[0]['deliveryDate'] = {"startDate": (now + timedelta(days=2)).isoformat(),
                                 "endDate": (now + timedelta(days=5)).isoformat()}

with open(os.path.join(here, 'data/tender_data.json')) as _in:
    test_tender_data = json.load(_in)
test_tender_data['procuringEntity'] = test_procuringEntity
test_tender_data['items'] = test_items

if SANDBOX_MODE:
    test_tender_data['procurementMethodDetails'] = 'quick, accelerator=1440'

for bid in test_bids:
    bid['tenderers'] = [test_organization]

with open(os.path.join(here, 'data/lots.json')) as _in:
    test_lots = json.load(_in)


test_agreement_features = deepcopy(test_agreement)
test_agreement_features['features'] = test_features

class BaseTenderWebTest(BaseTWT):
    initial_data = test_tender_data
    initial_agreement = deepcopy(test_agreement)
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
    periods = periods

    def update_periods(self, status, startend):
        LOT_PERIODS = ('auctionPeriod',)
        lots = self.tender_document.get('lots', [])

        for period in self.periods[status][startend]:
            self.tender_document_patch.update({period: {}})
            if period in LOT_PERIODS:
                continue
            for date in self.periods[status][startend][period]:
                self.tender_document_patch[period][date] = (
                    self.now + self.periods[status][startend][period][date]
                ).isoformat()

        if lots:
            for period in self.periods[status][startend]:
                if period in LOT_PERIODS:
                    for lot in lots:
                        if lot.get('status', None) == 'active':
                            lot.update({period: {}})
                            for date in self.periods[status][startend][period]:
                                lot[period][date] = (
                                    self.now + self.periods[status][startend][period][date]
                                ).isoformat()
            self.tender_document_patch.update({'lots': lots})
        self.save_changes()

    def check_chronograph(self):
        authorization = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.app.authorization = authorization
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

    def get_timedelta(self, **kw):
        delta = timedelta(**kw)
        if SANDBOX_MODE:
            delta = delta / 1440
        return delta

    def calculate_agreement_contracts_value_amount(self, agreement, items):
        for contract in agreement['contracts']:
            value = deepcopy(contract['unitPrices'][0]['value'])
            value['amount'] = 0
            for unitPrice in contract['unitPrices']:
                quantity = [i for i in items if i['id'] == unitPrice['relatedItem']][0]['quantity']
                value['amount'] += float(unitPrice['value']['amount']) * float(quantity)
            contract['value'] = value

    def patch_agreements_by_bot(self, status, start_end='start'):
        agreements = self.tender_document.get('agreements', [])
        for agreement in agreements:
            if 'agreementID' not in agreement:
                agreement.update(self.initial_agreement)
            items = self.tender_document.get('items')
            if items:
                self.calculate_agreement_contracts_value_amount(agreement, items)
        if 'features' in agreements[0]:
            self.tender_document_patch.update({'features': agreements[0]['features']})
        self.tender_document_patch.update({'agreements': agreements})

    def generate_bids(self, status, start_end='start'):
        bids = self.tender_document.get('bids', [])

        if not bids and self.initial_bids:
            self.tender_document_patch['bids'] = []
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
                self.tender_document_patch['bids'].append(bid)
            self.initial_bids = self.tender_document_patch['bids']
            bids = self.initial_bids
        if bids:
            self.bid_id = bids[0]['id']
            self.bid_token = bids[0]['owner_token']

    def generate_tender_lot_value(self, status, start_end='start'):
        agreements = self.tender_document.get('agreements', [])
        max_value = max([contract['value'] for contract in agreements[0]['contracts']],
                        key=lambda value: value['amount'])
        self.tender_document['value'] = max_value
        self.tender_document['lots'][0]['value'] = max_value
        self.tender_document['lots'][0]['minimalStep'] = deepcopy(max_value)
        self.tender_document['lots'][0]['minimalStep']['amount'] = \
            max_value['amount'] * TenderCfaSelectionUAConfigurator.minimal_step_percentage


    def generate_awards(self, status, start_end='start'):
        bids = self.tender_document.get('bids', []) or self.tender_document_patch.get('bids', [])
        lots = self.tender_document.get('lots', []) or self.tender_document_patch.get('lots', [])
        if 'awards' not in self.tender_document:
            self.tender_document_patch['awards'] = []
            if lots:
                active_lots = {lot['id']: 0 for lot in lots if lot['status'] == 'active'}
                self.tender_document_patch['awards'] = []
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
                            self.tender_document_patch['awards'].append(award)
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
                    self.tender_document_patch['awards'].append(award)

    def activate_awards_and_generate_contract(self, status, start_end='start'):
        awards = self.tender_document.get('awards', [])
        if not awards:
            awards = self.tender_document_patch.get('awards', [])
        for award in awards:
            if award['status'] == 'pending':
                award.update({'status': 'active'})
        self.tender_document_patch.update({'awards': awards})
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
                    self.tender_document_patch.update({'contracts': [contract]})

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
        self.now = get_now()
        self.tender_document = self.db.get(self.tender_id)
        self.tender_document_patch = {'status': status}

        if status == 'active.enquiries':
            self.update_periods(status, start_end)
            self.patch_agreements_by_bot(status, start_end)
            self.generate_tender_lot_value(status)
        elif status == 'active.tendering':
            self.update_periods(status, start_end)
            self.patch_agreements_by_bot(status, start_end)
            if start_end == 'end':
                self.generate_bids(status, start_end)
            self.generate_tender_lot_value(status)
        elif status == 'active.auction':
            self.update_periods(status, start_end)
            self.patch_agreements_by_bot(status, start_end)
            self.generate_bids(status, start_end)
            self.generate_tender_lot_value(status)
        elif status == 'active.qualification':
            self.update_periods(status, start_end)
            self.patch_agreements_by_bot(status, start_end)
            self.generate_bids(status, start_end)
            self.generate_tender_lot_value(status)
            self.generate_awards(status, start_end)
        elif status == 'active.awarded':
            self.update_periods(status, start_end)
            self.patch_agreements_by_bot(status, start_end)
            self.generate_bids(status, start_end)
            self.generate_tender_lot_value(status)
            self.generate_awards(status, start_end)
            self.activate_awards_and_generate_contract(status, start_end)
        elif status == 'complete':
            self.update_periods(status, start_end)
            self.patch_agreements_by_bot(status, start_end)
            self.generate_bids(status, start_end)
            self.generate_tender_lot_value(status)
            self.generate_awards(status, start_end)
            self.activate_awards_and_generate_contract(status, start_end)


        if extra:
            self.tender_document_patch.update(extra)

        self.save_changes()
        return self.get_tender('chronograph')

    def save_changes(self):
        if self.tender_document_patch:
            self.tender_document.update(apply_data_patch(self.tender_document, self.tender_document_patch))
            self.db.save(self.tender_document)
            self.tender_document = self.db.get(self.tender_id)
            self.tender_document_patch = {}


class TenderContentWebTest(BaseTenderWebTest):
    initial_data = test_tender_data
    initial_status = None
    initial_bids = None
    initial_lots = None

    def setUp(self):
        super(TenderContentWebTest, self).setUp()
        self.create_tender()
