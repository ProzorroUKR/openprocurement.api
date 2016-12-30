# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from openprocurement.api.tests.base import (
    BaseTenderWebTest, BaseWebTest
)

from openprocurement.tender.openua.tests.base import test_tender_data as base_ua_test_data
from openprocurement.tender.openeu.tests.base import test_tender_data as base_eu_test_data


test_tender_ua_data = deepcopy(base_ua_test_data)
test_tender_ua_data['procurementMethodType'] = "esco.UA"

test_tender_eu_data = deepcopy(base_eu_test_data)
test_tender_eu_data['procurementMethodType'] = "esco.EU"


class BaseESCOWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)


class BaseESCOContentWebTest(BaseESCOWebTest):
    initial_data = None
    initial_status = None
    initial_bids = None
    initial_lots = None
    initial_auth = ('Basic', ('broker', ''))
    docservice = None

    def setUp(self):
        super(BaseESCOContentWebTest, self).setUp()
        self.app.authorization = self.initial_auth
        self.couchdb_server = self.app.app.registry.couchdb_server
        self.db = self.app.app.registry.db
        if self.docservice:
            self.setUpDS()

    def tearDown(self):
        if self.docservice:
            self.tearDownDS()
        del self.couchdb_server[self.db.name]


class BaseESCOUAContentWebTest(BaseESCOContentWebTest):
    initial_data = test_tender_eu_data


class BaseESCOEUContentWebTest(BaseESCOContentWebTest):
    initial_data = test_tender_ua_data
