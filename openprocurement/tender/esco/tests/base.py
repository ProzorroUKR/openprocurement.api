# -*- coding: utf-8 -*-
import os
from uuid import uuid4
from copy import deepcopy
from datetime import timedelta
from openprocurement.api.constants import SANDBOX_MODE
from openprocurement.api.tests.base import (
    BaseWebTest, now
)
from openprocurement.api.utils import apply_data_patch, get_now
from openprocurement.tender.openeu.constants import (
    TENDERING_DURATION as TENDERING_DURATION_EU,
    QUESTIONS_STAND_STILL as QUESTIONS_STAND_STILL_EU,
    COMPLAINT_STAND_STILL as COMPLAINT_STAND_STILL_EU
)
from openprocurement.tender.openeu.tests.base import (
    test_tender_data as base_eu_test_data,
    test_lots as base_eu_lots,
    test_bids
)


test_tender_data = deepcopy(base_eu_test_data)
test_tender_data['procurementMethodType'] = "esco.EU"
test_tender_data['NBUdiscountRate'] = 0.22

test_tender_data['minValue'] = test_tender_data['value']
del test_tender_data['value']

test_lots = deepcopy(base_eu_lots)
test_lots[0]['minValue'] = test_lots[0]['value']
del test_lots[0]['value']


class BaseESCOWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = None
    initial_status = None
    initial_bids = None
    initial_lots = None
    initial_auth = ('Basic', ('broker', ''))
    docservice = None

    def setUp(self):
        super(BaseESCOWebTest, self).setUp()
        self.app.authorization = self.initial_auth
        self.couchdb_server = self.app.app.registry.couchdb_server
        self.db = self.app.app.registry.db
        if self.docservice:
            self.setUpDS()

    def tearDown(self):
        if self.docservice:
            self.tearDownDS()
        del self.couchdb_server[self.db.name]



class BaseESCOContentWebTest(BaseESCOWebTest):
    """ ESCO Content Test """
    initialize_initial_data = True
    forbidden_lot_actions_status = 'active.auction'  # status, in which operations with tender lots (adding, updating, deleting) are forbidden

    def setUp(self):
        super(BaseESCOContentWebTest, self).setUp()
        if self.initial_data and self.initialize_initial_data:
            self.create_tender()

    def create_tender(self):
        cur_auth = self.app.authorization
        self.app.authorization = self.initial_auth

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
        if self.initial_bids:
            self.initial_bids_tokens = {}
            response = self.set_status('active.tendering')
            status = response.json['data']['status']
            bids = []
            for i in self.initial_bids:
                if self.initial_lots:
                    i = i.copy()
                    value = i.pop('value')
                    i['lotValues'] = [
                        {
                            'value': value,
                            'relatedLot': l['id'],
                        }
                        for l in self.initial_lots
                    ]
                response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': i})
                self.assertEqual(response.status, '201 Created')
                bids.append(response.json['data'])
                self.initial_bids_tokens[response.json['data']['id']] = response.json['access']['token']
            self.initial_bids = bids
        if self.initial_status != status:
            self.set_status(self.initial_status)

        self.app.authorization = cur_auth


class BaseESCOEUContentWebTest(BaseESCOContentWebTest):
    """ ESCO EU Content Test """

    initial_data = test_tender_data

    def set_status(self, status, extra=None):
        data = {'status': status}
        if status == 'active.tendering':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now - timedelta(days=1)).isoformat(),
                    "endDate": (now + TENDERING_DURATION_EU - QUESTIONS_STAND_STILL_EU).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - timedelta(days=1)).isoformat(),
                    "endDate": (now + TENDERING_DURATION_EU).isoformat()
                }
            })
        elif status == 'active.pre-qualification':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now - TENDERING_DURATION_EU - timedelta(days=1)).isoformat(),
                    "endDate": (now - QUESTIONS_STAND_STILL_EU).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - TENDERING_DURATION_EU - timedelta(days=1)).isoformat(),
                    "endDate": (now).isoformat(),
                },
                "qualificationPeriod": {
                    "startDate": (now).isoformat(),
                }
            })
        elif status == 'active.pre-qualification.stand-still':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now - TENDERING_DURATION_EU - timedelta(days=1)).isoformat(),
                    "endDate": (now - QUESTIONS_STAND_STILL_EU).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - TENDERING_DURATION_EU - timedelta(days=1)).isoformat(),
                    "endDate": (now).isoformat(),
                },
                "qualificationPeriod": {
                    "startDate": (now).isoformat(),
                },
                "auctionPeriod": {
                    "startDate": (now + COMPLAINT_STAND_STILL_EU).isoformat()
                }
            })
        elif status == 'active.auction':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now - TENDERING_DURATION_EU - COMPLAINT_STAND_STILL_EU - timedelta(days=1)).isoformat(),
                    "endDate": (now - COMPLAINT_STAND_STILL_EU - TENDERING_DURATION_EU + QUESTIONS_STAND_STILL_EU).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - TENDERING_DURATION_EU - COMPLAINT_STAND_STILL_EU - timedelta(days=1)).isoformat(),
                    "endDate": (now - COMPLAINT_STAND_STILL_EU).isoformat()
                },
                "qualificationPeriod": {
                    "startDate": (now - COMPLAINT_STAND_STILL_EU).isoformat(),
                    "endDate": (now).isoformat()
                },
                "auctionPeriod": {
                    "startDate": (now).isoformat()
                }
            })
            if self.initial_lots:
                data.update({
                    'lots': [
                        {
                            "auctionPeriod": {
                                "startDate": (now).isoformat()
                            }
                        }
                        for i in self.initial_lots
                    ]
                })
        elif status == 'active.qualification':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now - TENDERING_DURATION_EU - COMPLAINT_STAND_STILL_EU - timedelta(days=2)).isoformat(),
                    "endDate": (now - QUESTIONS_STAND_STILL_EU - COMPLAINT_STAND_STILL_EU - timedelta(days=1)).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - TENDERING_DURATION_EU - COMPLAINT_STAND_STILL_EU - timedelta(days=2)).isoformat(),
                    "endDate": (now - COMPLAINT_STAND_STILL_EU - timedelta(days=1)).isoformat()
                },
                "auctionPeriod": {
                    "startDate": (now - timedelta(days=1)).isoformat(),
                    "endDate": (now).isoformat()
                },
                "awardPeriod": {
                    "startDate": (now).isoformat()
                }
            })
            if self.initial_lots:
                data.update({
                    'lots': [
                        {
                            "auctionPeriod": {
                                "startDate": (now - timedelta(days=1)).isoformat(),
                                "endDate": (now).isoformat()
                            }
                        }
                        for i in self.initial_lots
                    ]
                })
        elif status == 'active.awarded':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now - TENDERING_DURATION_EU - COMPLAINT_STAND_STILL_EU - timedelta(days=3)).isoformat(),
                    "endDate": (now - QUESTIONS_STAND_STILL_EU - COMPLAINT_STAND_STILL_EU - timedelta(days=2)).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - TENDERING_DURATION_EU - COMPLAINT_STAND_STILL_EU - timedelta(days=3)).isoformat(),
                    "endDate": (now - COMPLAINT_STAND_STILL_EU - timedelta(days=2)).isoformat()
                },
                "auctionPeriod": {
                    "startDate": (now - timedelta(days=2)).isoformat(),
                    "endDate": (now - timedelta(days=1)).isoformat()
                },
                "awardPeriod": {
                    "startDate": (now - timedelta(days=1)).isoformat(),
                    "endDate": (now).isoformat()
                }
            })
            if self.initial_lots:
                data.update({
                    'lots': [
                        {
                            "auctionPeriod": {
                                "startDate": (now - timedelta(days=2)).isoformat(),
                                "endDate": (now - timedelta(days=1)).isoformat()
                            }
                        }
                        for i in self.initial_lots
                    ]
                })
        elif status == 'complete':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now - TENDERING_DURATION_EU - COMPLAINT_STAND_STILL_EU - timedelta(days=4)).isoformat(),
                    "endDate": (now - QUESTIONS_STAND_STILL_EU - COMPLAINT_STAND_STILL_EU - timedelta(days=3)).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - TENDERING_DURATION_EU - COMPLAINT_STAND_STILL_EU - timedelta(days=4)).isoformat(),
                    "endDate": (now - COMPLAINT_STAND_STILL_EU - timedelta(days=3)).isoformat()
                },
                "auctionPeriod": {
                    "startDate": (now - timedelta(days=3)).isoformat(),
                    "endDate": (now - timedelta(days=2)).isoformat()
                },
                "awardPeriod": {
                    "startDate": (now - timedelta(days=1)).isoformat(),
                    "endDate": (now).isoformat()
                }
            })
            if self.initial_lots:
                data.update({
                    'lots': [
                        {
                            "auctionPeriod": {
                                "startDate": (now - timedelta(days=3)).isoformat(),
                                "endDate": (now - timedelta(days=2)).isoformat()
                            }
                        }
                        for i in self.initial_lots
                    ]
                })
        if extra:
            data.update(extra)

        tender = self.db.get(self.tender_id)
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


    def go_to_enquiryPeriod_end(self):
        now = get_now()
        self.set_status('active.tendering', {
            "enquiryPeriod": {
                "startDate": (now - timedelta(days=28)).isoformat(),
                "endDate": (now - (timedelta(minutes=1) if SANDBOX_MODE else timedelta(days=1))).isoformat()
            },
            "tenderPeriod": {
                "startDate": (now - timedelta(days=28)).isoformat(),
                "endDate": (now + (timedelta(minutes=2) if SANDBOX_MODE else timedelta(days=2))).isoformat()
            }
        })


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
                "enquiryPeriod": {
                    "startDate": (now - timedelta(days=28)).isoformat(),
                    "endDate": (now - timedelta(days=1)).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - timedelta(days=28)).isoformat(),
                    "endDate": (now + timedelta(days=2)).isoformat()
                },
            })
        if status == 'active.pre-qualification':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now - TENDERING_DURATION_EU).isoformat(),
                    "endDate": (now - QUESTIONS_STAND_STILL_EU).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - TENDERING_DURATION_EU).isoformat(),
                    "endDate": (now).isoformat(),
                }
            })
        elif status == 'active.pre-qualification.stand-still':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now - TENDERING_DURATION_EU).isoformat(),
                    "endDate": (now - QUESTIONS_STAND_STILL_EU).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - TENDERING_DURATION_EU).isoformat(),
                    "endDate": (now).isoformat(),
                },
                "qualificationPeriod": {
                    "startDate": (now).isoformat(),
                },
            })
            if 'lots' in tender and tender['lots']:
                data['lots'] = []
                for index, lot in enumerate(tender['lots']):
                    lot_data = {'id': lot['id']}
                    if lot['status'] is 'active':
                        lot_data["auctionPeriod"] = {
                        "startDate": (now + COMPLAINT_STAND_STILL_EU).isoformat()
                    }
                    data['lots'].append(lot_data)
            else:
                data.update({
                    "auctionPeriod": {
                        "startDate": (now + COMPLAINT_STAND_STILL_EU).isoformat()
                    }
                })
        elif status == 'active.auction':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now - TENDERING_DURATION_EU - COMPLAINT_STAND_STILL_EU).isoformat(),
                    "endDate": (now - COMPLAINT_STAND_STILL_EU - TENDERING_DURATION_EU + QUESTIONS_STAND_STILL_EU).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - TENDERING_DURATION_EU - COMPLAINT_STAND_STILL_EU).isoformat(),
                    "endDate": (now - COMPLAINT_STAND_STILL_EU).isoformat()
                },
                "qualificationPeriod": {
                    "startDate": (now - COMPLAINT_STAND_STILL_EU).isoformat(),
                    "endDate": (now).isoformat()
                }
            })
            if 'lots' in tender and tender['lots']:
                data['lots'] = []
                for index, lot in enumerate(tender['lots']):
                    lot_data = {'id': lot['id']}
                    if lot['status'] == 'active':
                        lot_data["auctionPeriod"] = {
                            "startDate": (now).isoformat()
                        }
                    data['lots'].append(lot_data)
            else:
                data.update({
                    "auctionPeriod": {
                        "startDate": now.isoformat()
                    }
                })
        elif status == 'complete':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now - TENDERING_DURATION_EU - COMPLAINT_STAND_STILL_EU - timedelta(days=3)).isoformat(),
                    "endDate": (now - QUESTIONS_STAND_STILL_EU - COMPLAINT_STAND_STILL_EU - timedelta(days=3)).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - TENDERING_DURATION_EU - COMPLAINT_STAND_STILL_EU - timedelta(days=3)).isoformat(),
                    "endDate": (now - COMPLAINT_STAND_STILL_EU - timedelta(days=3)).isoformat()
                },
                "auctionPeriod": {
                    "startDate": (now - timedelta(days=3)).isoformat(),
                    "endDate": (now - timedelta(days=2)).isoformat()
                },
                "awardPeriod": {
                    "startDate": (now - timedelta(days=1)).isoformat(),
                    "endDate": (now).isoformat()
                }
            })
            if self.initial_lots:
                data.update({
                    'lots': [
                        {
                            "auctionPeriod": {
                                "startDate": (now - timedelta(days=3)).isoformat(),
                                "endDate": (now - timedelta(days=2)).isoformat()
                            }
                        }
                        for i in self.initial_lots
                    ]
                })
        if extra:
            data.update(extra)
        tender.update(apply_data_patch(tender, data))
        self.db.save(tender)
