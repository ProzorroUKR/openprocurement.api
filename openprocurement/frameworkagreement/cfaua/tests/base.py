# -*- coding: utf-8 -*-

import os, json
from copy import deepcopy
from datetime import datetime, timedelta
from openprocurement.api.constants import SANDBOX_MODE
from openprocurement.tender.openua.tests.base import (
    BaseTenderUAWebTest as BaseBaseTenderWebTest
)
from openprocurement.api.utils import apply_data_patch, get_now
from openprocurement.frameworkagreement.cfaua.constants import (
    TENDERING_DAYS,
    TENDERING_DURATION,
    QUESTIONS_STAND_STILL,
    COMPLAINT_STAND_STILL,
    STAND_STILL_TIME,
    MIN_BIDS_NUMBER
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
now = datetime.now()

# Prepare test_bids_data
with open(os.path.join(BASE_DIR, 'data/test_bids.json')) as fd:
   test_bids = json.load(fd)
   test_bids = [deepcopy(test_bids[0]) for _ in range(MIN_BIDS_NUMBER)]
   for num, test_bid in enumerate(test_bids):
       test_bid['value']['amount'] = test_bid['value']['amount'] + num * 1

# Prepare test_features_tender_data
with open(os.path.join(BASE_DIR, 'data/test_tender.json')) as fd:
    test_tender_data = json.load(fd)
    test_tender_data['tenderPeriod']['endDate'] = (now + timedelta(days=TENDERING_DAYS+1)).isoformat()

if SANDBOX_MODE:
    test_tender_data['procurementMethodDetails'] = 'quick, accelerator=1440'


# Prepare features_tender
with open(os.path.join(BASE_DIR, 'data/test_features.json')) as fd:
    test_features_tender_data = test_tender_data.copy()
    test_features_item = test_features_tender_data['items'][0].copy()
    test_features_item['id'] = '1'
    test_features_tender_data['items'] = [test_features_item]
    test_features_tender_data['features'] = json.load(fd)

# Prepare features_tender
with open(os.path.join(BASE_DIR, 'data/test_lots.json')) as fd:
    test_lots = json.load(fd)


class BaseTenderWebTest(BaseBaseTenderWebTest):
    min_bids_number = MIN_BIDS_NUMBER
    initial_data = test_tender_data
    initial_status = None
    initial_bids = None
    initial_lots = None
    initial_auth = None
    relative_to = os.path.dirname(__file__)
    forbidden_agreement_document_modification_actions_status = 'unsuccessful'  # status, in which operations with tender's contract documents (adding, updating) are forbidden
    forbidden_question_modification_actions_status = 'active.pre-qualification'  # status, in which adding/updating tender questions is forbidden
    question_claim_block_status = 'active.pre-qualification'  # status, tender cannot be switched to while it has questions/complaints related to its lot
    # auction role actions
    forbidden_auction_actions_status = 'active.pre-qualification.stand-still'  # status, in which operations with tender auction (getting auction info, reporting auction results, updating auction urls) and adding tender documents are forbidden
    forbidden_auction_document_create_actions_status = 'active.pre-qualification.stand-still'  # status, in which adding document to tender auction is forbidden

    def go_to_enquiryPeriod_end(self):
        now = get_now()
        self.set_status('active.tendering', {
            'enquiryPeriod': {
                'startDate': (now - timedelta(days=28)).isoformat(),
                'endDate': (now - (timedelta(minutes=1) if SANDBOX_MODE else timedelta(days=1))).isoformat()
            },
            'tenderPeriod': {
                'startDate': (now - timedelta(days=28)).isoformat(),
                'endDate': (now + (timedelta(minutes=2) if SANDBOX_MODE else timedelta(days=2))).isoformat()
            }
        })

    def setUp(self):
        super(BaseBaseTenderWebTest, self).setUp()
        if self.initial_auth:
            self.app.authorization = self.initial_auth
        else:
            self.app.authorization = ('Basic', ('token', ''))
        self.couchdb_server = self.app.app.registry.couchdb_server
        self.db = self.app.app.registry.db
        if self.docservice:
            self.setUpDS()

    def tearDown(self):
        if self.docservice:
            self.tearDownDS()
        del self.couchdb_server[self.db.name]

    def check_chronograph(self):
        authorization = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        self.app.authorization = authorization
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')

    def time_shift(self, status, extra=None):
        now = get_now()
        tender = self.db.get(self.tender_id)
        data = {}
        if status == 'enquiryPeriod_ends':
            data.update({
                'enquiryPeriod': {
                    'startDate': (now - timedelta(days=28)).isoformat(),
                    'endDate': (now - timedelta(days=1)).isoformat()
                },
                'tenderPeriod': {
                    'startDate': (now - timedelta(days=28)).isoformat(),
                    'endDate': (now + timedelta(days=2)).isoformat()
                },
            })
        if status == 'active.pre-qualification':
            data.update({
                'enquiryPeriod': {
                    'startDate': (now - TENDERING_DURATION).isoformat(),
                    'endDate': (now - QUESTIONS_STAND_STILL).isoformat()
                },
                'tenderPeriod': {
                    'startDate': (now - TENDERING_DURATION).isoformat(),
                    'endDate': (now).isoformat(),
                }
            })
        elif status == 'active.pre-qualification.stand-still':
            data.update({
                'enquiryPeriod': {
                    'startDate': (now - TENDERING_DURATION).isoformat(),
                    'endDate': (now - QUESTIONS_STAND_STILL).isoformat()
                },
                'tenderPeriod': {
                    'startDate': (now - TENDERING_DURATION).isoformat(),
                    'endDate': (now).isoformat(),
                },
                'qualificationPeriod': {
                    'startDate': (now).isoformat(),
                },
            })
            if 'lots' in tender and tender['lots']:
                data['lots'] = []
                for index, lot in enumerate(tender['lots']):
                    lot_data = {'id': lot['id']}
                    if lot['status'] is 'active':
                        lot_data['auctionPeriod'] = {
                        'startDate': (now + COMPLAINT_STAND_STILL).isoformat()
                    }
                    data['lots'].append(lot_data)
            else:
                data.update({
                    'auctionPeriod': {
                        'startDate': (now + COMPLAINT_STAND_STILL).isoformat()
                    }
                })
        elif status == 'active.auction':
            data.update({
                'enquiryPeriod': {
                    'startDate': (now - TENDERING_DURATION - COMPLAINT_STAND_STILL).isoformat(),
                    'endDate': (now - COMPLAINT_STAND_STILL - TENDERING_DURATION + QUESTIONS_STAND_STILL).isoformat()
                },
                'tenderPeriod': {
                    'startDate': (now - TENDERING_DURATION - COMPLAINT_STAND_STILL).isoformat(),
                    'endDate': (now - COMPLAINT_STAND_STILL).isoformat()
                },
                'qualificationPeriod': {
                    'startDate': (now - COMPLAINT_STAND_STILL).isoformat(),
                    'endDate': (now).isoformat()
                }
            })
            if 'lots' in tender and tender['lots']:
                data['lots'] = []
                for index, lot in enumerate(tender['lots']):
                    lot_data = {'id': lot['id']}
                    if lot['status'] == 'active':
                        lot_data['auctionPeriod'] = {
                            'startDate': (now).isoformat()
                        }
                    data['lots'].append(lot_data)
            else:
                data.update({
                    'auctionPeriod': {
                        'startDate': now.isoformat()
                    }
                })
        elif status == 'complete':
            data.update({
                'enquiryPeriod': {
                    'startDate': (now - TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=3)).isoformat(),
                    'endDate': (now - QUESTIONS_STAND_STILL - COMPLAINT_STAND_STILL - timedelta(days=3)).isoformat()
                },
                'tenderPeriod': {
                    'startDate': (now - TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=3)).isoformat(),
                    'endDate': (now - COMPLAINT_STAND_STILL - timedelta(days=3)).isoformat()
                },
                'auctionPeriod': {
                    'startDate': (now - timedelta(days=3)).isoformat(),
                    'endDate': (now - timedelta(days=2)).isoformat()
                },
                'awardPeriod': {
                    'startDate': (now - timedelta(days=1)).isoformat(),
                    'endDate': (now).isoformat()
                }
            })
            if self.initial_lots:
                data.update({
                    'lots': [
                        {
                            'auctionPeriod': {
                                'startDate': (now - timedelta(days=3)).isoformat(),
                                'endDate': (now - timedelta(days=2)).isoformat()
                            }
                        }
                        for i in self.initial_lots
                    ]
                })
        if extra:
            data.update(extra)
        tender.update(apply_data_patch(tender, data))
        self.db.save(tender)

    def set_status(self, status, extra=None):
        tender = self.db.get(self.tender_id)

        def activate_bids():
            if tender.get('bids', ''):
                bids = tender['bids']
                for bid in bids:
                    if bid['status'] == 'pending':
                        bid.update({'status': 'active'})
                data.update({'bids': bids})

        def activate_awards():
            if tender.get('awards', []):
                awards = tender['awards']
                for award in awards:
                    if award['status'] == 'pending':
                        award.update({'status': 'active'})
                    award.update({
                        'complaintPeriod': {
                            'startDate': now.isoformat(),
                            'endDate': (now + timedelta(days=7)).isoformat()
                        }
                    })
                data.update({'awards': awards})

        data = {'status': status}
        if status == 'active.tendering':
            data.update({
                'enquiryPeriod': {
                    'startDate': (now - timedelta(days=1)).isoformat(),
                    'endDate': (now + TENDERING_DURATION - QUESTIONS_STAND_STILL).isoformat()
                },
                'tenderPeriod': {
                    'startDate': (now - timedelta(days=1)).isoformat(),
                    'endDate': (now + TENDERING_DURATION).isoformat()
                }
            })
        elif status == 'active.pre-qualification':
            data.update({
                'enquiryPeriod': {
                    'startDate': (now - TENDERING_DURATION - timedelta(days=1)).isoformat(),
                    'endDate': (now - QUESTIONS_STAND_STILL).isoformat()
                },
                'tenderPeriod': {
                    'startDate': (now - TENDERING_DURATION - timedelta(days=1)).isoformat(),
                    'endDate': (now).isoformat(),
                },
                'qualificationPeriod': {
                    'startDate': (now).isoformat(),
                }
            })
        elif status == 'active.pre-qualification.stand-still':
            data.update({
                'enquiryPeriod': {
                    'startDate': (now - TENDERING_DURATION - timedelta(days=1)).isoformat(),
                    'endDate': (now - QUESTIONS_STAND_STILL).isoformat()
                },
                'tenderPeriod': {
                    'startDate': (now - TENDERING_DURATION - timedelta(days=1)).isoformat(),
                    'endDate': (now).isoformat(),
                },
                'qualificationPeriod': {
                    'startDate': (now).isoformat(),
                },
                'auctionPeriod': {
                    'startDate': (now + COMPLAINT_STAND_STILL).isoformat()
                }
            })
            activate_bids()
        elif status == 'active.auction':
            data.update({
                'enquiryPeriod': {
                    'startDate': (now - TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=1)).isoformat(),
                    'endDate': (now - COMPLAINT_STAND_STILL - TENDERING_DURATION + QUESTIONS_STAND_STILL).isoformat()
                },
                'tenderPeriod': {
                    'startDate': (now - TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=1)).isoformat(),
                    'endDate': (now - COMPLAINT_STAND_STILL).isoformat()
                },
                'qualificationPeriod': {
                    'startDate': (now - COMPLAINT_STAND_STILL).isoformat(),
                    'endDate': (now).isoformat()
                },
                'auctionPeriod': {
                    'startDate': (now).isoformat()
                }
            })
            if self.initial_lots:
                data.update({
                    'lots': [
                        {
                            'auctionPeriod': {
                                'startDate': (now).isoformat()
                            }
                        }
                        for i in self.initial_lots
                    ]
                })
            activate_bids()
        elif status == 'active.qualification':
            
            data.update({
                'enquiryPeriod': {
                    'startDate': (now - TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=2)).isoformat(),
                    'endDate': (now - QUESTIONS_STAND_STILL - COMPLAINT_STAND_STILL - timedelta(days=1)).isoformat()
                },
                'tenderPeriod': {
                    'startDate': (now - TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=2)).isoformat(),
                    'endDate': (now - COMPLAINT_STAND_STILL - timedelta(days=1)).isoformat()
                },
                'auctionPeriod': {
                    'startDate': (now - timedelta(days=1)).isoformat(),
                    'endDate': (now).isoformat()
                },
                'awardPeriod': {
                    'startDate': (now).isoformat()
                }
            })
            activate_bids()
            if self.initial_lots:
                data.update({
                    'lots': [
                        {
                            'auctionPeriod': {
                                'startDate': (now - timedelta(days=1)).isoformat(),
                                'endDate': (now).isoformat()
                            }
                        }
                        for i in self.initial_lots
                    ]
                })
        elif status == 'active.qualification.stand-still':
            data.update({
                'enquiryPeriod': {
                    'startDate': (now - TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=2)).isoformat(),
                    'endDate': (now - QUESTIONS_STAND_STILL - COMPLAINT_STAND_STILL - timedelta(days=1)).isoformat()
                },
                'tenderPeriod': {
                    'startDate': (now - TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=2)).isoformat(),
                    'endDate': (now - COMPLAINT_STAND_STILL - timedelta(days=1)).isoformat()
                },
                'auctionPeriod': {
                    'startDate': (now - timedelta(days=1)).isoformat(),
                    'endDate': (now).isoformat()
                },
                'awardPeriod': {
                    'startDate': now.isoformat(),
                    'endDate': (now + STAND_STILL_TIME).isoformat()
                }
            })
            activate_awards()
        elif status == 'active.awarded':
            data.update({
                'enquiryPeriod': {
                    'startDate': (now - TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=3)).isoformat(),
                    'endDate': (now - QUESTIONS_STAND_STILL - COMPLAINT_STAND_STILL - timedelta(days=2)).isoformat()
                },
                'tenderPeriod': {
                    'startDate': (now - TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=3)).isoformat(),
                    'endDate': (now - COMPLAINT_STAND_STILL - timedelta(days=2)).isoformat()
                },
                'auctionPeriod': {
                    'startDate': (now - timedelta(days=2)).isoformat(),
                    'endDate': (now - timedelta(days=1)).isoformat()
                },
                'awardPeriod': {
                    'startDate': (now - timedelta(days=1)).isoformat(),
                    'endDate': (now).isoformat()
                }
            })
            activate_bids()
            if self.initial_lots:
                data.update({
                    'lots': [
                        {
                            'auctionPeriod': {
                                'startDate': (now - timedelta(days=2)).isoformat(),
                                'endDate': (now - timedelta(days=1)).isoformat()
                            }
                        }
                        for i in self.initial_lots
                    ]
                })
        elif status == 'complete':
            data.update({
                'enquiryPeriod': {
                    'startDate': (now - TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=4)).isoformat(),
                    'endDate': (now - QUESTIONS_STAND_STILL - COMPLAINT_STAND_STILL - timedelta(days=3)).isoformat()
                },
                'tenderPeriod': {
                    'startDate': (now - TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=4)).isoformat(),
                    'endDate': (now - COMPLAINT_STAND_STILL - timedelta(days=3)).isoformat()
                },
                'auctionPeriod': {
                    'startDate': (now - timedelta(days=3)).isoformat(),
                    'endDate': (now - timedelta(days=2)).isoformat()
                },
                'awardPeriod': {
                    'startDate': (now - timedelta(days=1)).isoformat(),
                    'endDate': (now).isoformat()
                }
            })
            if self.initial_lots:
                data.update({
                    'lots': [
                        {
                            'auctionPeriod': {
                                'startDate': (now - timedelta(days=3)).isoformat(),
                                'endDate': (now - timedelta(days=2)).isoformat()
                            }
                        }
                        for i in self.initial_lots
                    ]
                })
        if extra:
            data.update(extra)

        tender.update(apply_data_patch(tender, data))
        self.db.save(tender)

        authorization = self.app.authorization
        self.app.authorization = ('Basic', ('chronograph', ''))
        #response = self.app.patch_json('/tenders/{}'.format(self.tender_id), {'data': {'id': self.tender_id}})
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.app.authorization = authorization
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        return response

    def prepare_award(self):
        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {'id': self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        # qualify bids
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.app.authorization = ('Basic', ('broker', ''))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}?acc_token={}'.format(
                self.tender_id, qualification['id'], self.tender_token),
                {'data': {'status': 'active', 'qualified': True, 'eligible': True}})
            self.assertEqual(response.status, '200 OK')

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
            self.tender_id, self.tender_token), {'data': {'status': 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        # switch to active.auction
        self.set_status('active.auction', {'id': self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {'data': {'id': self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.auction')

        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        for lot_id in self.initial_lots:
            response = self.app.post_json('/tenders/{}/auction/{}'.format(self.tender_id, lot_id['id']),
                                          {'data': {'bids': auction_bids_data}})
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/json')
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], 'active.qualification')


class BaseTenderContentWebTest(BaseTenderWebTest):
    initial_data = test_tender_data
    initial_status = None
    initial_bids = None
    initial_lots = None
    relative_to = os.path.dirname(__file__)

    def setUp(self):
        super(BaseTenderContentWebTest, self).setUp()
        self.create_tender()
