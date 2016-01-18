# -*- coding: utf-8 -*-
import os
import webtest
from datetime import datetime
from openprocurement.api.tests.base import test_tender_data as base_data
from openprocurement.api.tests.base import BaseTenderWebTest, PrefixedRequestClass


now = datetime.now()
test_tender_data = base_data.copy()

test_tender_data['title_en'] = "Cases for state awards"

test_tender_data['procurementMethodType'] = "aboveThresholdEU"


class BaseTenderWebTest(BaseTenderWebTest):
    initial_data = test_tender_data
    initial_status = None
    initial_bids = None
    initial_lots = None

    def setUp(self):
        self.app = webtest.TestApp(
            "config:tests.ini", relative_to=os.path.dirname(__file__))
        self.app.RequestClass = PrefixedRequestClass
        self.app.authorization = ('Basic', ('token', ''))
        self.couchdb_server = self.app.app.registry.couchdb_server
        self.db = self.app.app.registry.db

    def tearDown(self):
        del self.couchdb_server[self.db.name]


class BaseTenderContentWebTest(BaseTenderWebTest):
    initial_data = test_tender_data
    initial_status = None
    initial_bids = None
    initial_lots = None

    def setUp(self):
        super(BaseTenderContentWebTest, self).setUp()
        self.create_tender()
