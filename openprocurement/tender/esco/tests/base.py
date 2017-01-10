# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from openprocurement.api.tests.base import (
    BaseTenderWebTest, BaseWebTest
)

from openprocurement.api.tests.base import test_organization as base_test_organization
from openprocurement.tender.openua.tests.base import test_bids as base_test_bids
from openprocurement.tender.openua.tests.base import test_tender_data as base_ua_test_data
from openprocurement.tender.openeu.tests.base import test_tender_data as base_eu_test_data
from openprocurement.tender.limited.tests.base import test_tender_data as base_reporting_test_data


test_tender_ua_data = deepcopy(base_ua_test_data)
test_tender_ua_data['procurementMethodType'] = "esco.UA"

test_tender_eu_data = deepcopy(base_eu_test_data)
test_tender_eu_data['procurementMethodType'] = "esco.EU"

test_tender_reporting_data = deepcopy(base_reporting_test_data)
test_tender_reporting_data['procurementMethodType'] = "esco.reporting"

test_bids = deepcopy(base_test_bids)
test_organization = deepcopy(base_test_organization)


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

    def setUp(self):
        super(BaseESCOContentWebTest, self).setUp()
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

    def set_status(self, status):
        return


class BaseESCOUAContentWebTest(BaseESCOContentWebTest):
    """ ESCO UA Content Test """

    initial_data = test_tender_ua_data


class BaseESCOEUContentWebTest(BaseESCOContentWebTest):
    """ ESCO EU Content Test """

    initial_data = test_tender_eu_data


class BaseESCOReportingContentWebTest(BaseESCOContentWebTest):
    """ ESCO Reporting Content Test """

    initial_data = test_tender_reporting_data
