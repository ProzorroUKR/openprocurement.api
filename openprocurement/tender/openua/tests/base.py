# -*- coding: utf-8 -*-
import os
import webtest
from openprocurement.api.tests.base import (test_tender_data,
                                            test_features_tender_data,
                                            BaseTenderWebTest,
                                            PrefixedRequestClass)


test_tender_ua_data = test_tender_data.copy()
test_tender_ua_data['procurementMethodType'] = "aboveThresholdUA"
# test_tender_ua_data['magicUnicorns'] = 15

test_features_tender_ua_data = test_features_tender_data.copy()
test_features_tender_ua_data['procurementMethodType'] = "aboveThresholdUA"
# test_features_tender_ua_data['magicUnicorns'] = 15


class BaseTenderUAWebTest(BaseTenderWebTest):
    initial_data = test_tender_ua_data
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


class BaseTenderUAContentWebTest(BaseTenderUAWebTest):
    initial_data = test_tender_ua_data
    initial_status = None
    initial_bids = None
    initial_lots = None

    def setUp(self):
        super(BaseTenderUAContentWebTest, self).setUp()
        self.create_tender()
