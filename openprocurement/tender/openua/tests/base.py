# -*- coding: utf-8 -*-
import os
import webtest
from datetime import datetime, timedelta
from openprocurement.api.tests.base import (test_tender_data,
                                            now,
                                            test_features_tender_data,
                                            BaseTenderWebTest,
                                            PrefixedRequestClass)


test_tender_ua_data = test_tender_data.copy()
test_tender_ua_data['procurementMethodType'] = "aboveThresholdUA"
test_tender_ua_data["enquiryPeriod"] = {
        "endDate": (now + timedelta(days=16)).isoformat()
}

test_tender_ua_data["tenderPeriod"] = test_tender_ua_data["enquiryPeriod"].copy()

test_features_tender_ua_data = test_features_tender_data.copy()
test_features_tender_ua_data['procurementMethodType'] = "aboveThresholdUA"
test_features_tender_ua_data["enquiryPeriod"] = {
        "endDate": (now + timedelta(days=16)).isoformat()
}
test_features_tender_ua_data["tenderPeriod"] = test_features_tender_ua_data["enquiryPeriod"].copy()


from openprocurement.api.utils import VERSION, apply_data_patch

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

    def set_status(self, status, extra=None):
        data = {'status': status}
        if status == 'active.tendering':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now).isoformat(),
                    "endDate": (now + timedelta(days=13)).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now).isoformat(),
                    "endDate": (now + timedelta(days=16)).isoformat()
                }
            })
        elif status == 'active.auction':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now - timedelta(days=16)).isoformat(),
                    "endDate": (now - timedelta(days=3)).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - timedelta(days=16)).isoformat(),
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
                    "startDate": (now - timedelta(days=17)).isoformat(),
                    "endDate": (now - timedelta(days=4)).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - timedelta(days=17)).isoformat(),
                    "endDate": (now - timedelta(days=1)).isoformat()
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
                    "startDate": (now - timedelta(days=17)).isoformat(),
                    "endDate": (now - timedelta(days=4)).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - timedelta(days=17)).isoformat(),
                    "endDate": (now - timedelta(days=1)).isoformat()
                },
                "auctionPeriod": {
                    "startDate": (now - timedelta(days=1)).isoformat(),
                    "endDate": (now).isoformat()
                },
                "awardPeriod": {
                    "startDate": (now).isoformat(),
                    "endDate": (now).isoformat()
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
        elif status == 'complete':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now - timedelta(days=25)).isoformat(),
                    "endDate": (now - timedelta(days=11)).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - timedelta(days=25)).isoformat(),
                    "endDate": (now - timedelta(days=8)).isoformat()
                },
                "auctionPeriod": {
                    "startDate": (now - timedelta(days=8)).isoformat(),
                    "endDate": (now - timedelta(days=7)).isoformat()
                },
                "awardPeriod": {
                    "startDate": (now - timedelta(days=7)).isoformat(),
                    "endDate": (now - timedelta(days=7)).isoformat()
                }
            })
            if self.initial_lots:
                data.update({
                    'lots': [
                        {
                            "auctionPeriod": {
                                "startDate": (now - timedelta(days=8)).isoformat(),
                                "endDate": (now - timedelta(days=7)).isoformat()
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
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.app.authorization = authorization
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        return response


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
