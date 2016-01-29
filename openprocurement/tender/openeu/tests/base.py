# -*- coding: utf-8 -*-
import os
import webtest
from datetime import datetime, timedelta
from openprocurement.api.tests.base import BaseTenderWebTest, PrefixedRequestClass
from openprocurement.api.utils import apply_data_patch
from openprocurement.tender.openeu.models import TENDERING_DAYS, TENDERING_DURATION, QUESTIONS_STAND_STILL, COMPLAINT_STAND_STILL


now = datetime.now()
test_tender_data = {
    "title": u"футляри до державних нагород",
    "title_en": u"Cases for state awards",
    "procuringEntity": {
        "name": u"Державне управління справами",
        "name_en": u"State administration",
        "identifier": {
            "legalName_en": u"dus.gov.ua",
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
            "name_en": u"State administration",
            "availableLanguage": u"Ukraine",
            "telephone": u"0440000000"
        },
        "additionalContactPoints": [{
            "name": u"Державне управління справами",
            "name_en": u"State administration",
            "availableLanguage": u"English",
            "telephone": u"1440000000"
        }]
    },
    "value": {
        "amount": 500,
        "currency": u"UAH"
    },
    "minimalStep": {
        "amount": 35,
        "currency": u"UAH"
    },
    "items": [
        {
            "description": u"футляри до державних нагород",
            "description_en": u"Cases for state awards",
            "classification": {
                "scheme": u"CPV",
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
            "quantity": 5
        }
    ],
    "tenderPeriod": {
        "startDate": (now).isoformat(),
        "endDate": (now + timedelta(days=TENDERING_DAYS+1)).isoformat()
    },
    "procurementMethodType": "aboveThresholdEU",
}



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

    def set_status(self, status, extra=None):
        data = {'status': status}
        if status == 'active.tendering':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now).isoformat(),
                    "endDate": (now + TENDERING_DURATION - QUESTIONS_STAND_STILL).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now).isoformat(),
                    "endDate": (now + TENDERING_DURATION).isoformat()
                }
            })
        elif status == 'active.pre-qualification':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now - TENDERING_DURATION).isoformat(),
                    "endDate": (now - QUESTIONS_STAND_STILL).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - TENDERING_DURATION).isoformat(),
                    "endDate": (now).isoformat(),
                },
                "qualificationPeriod": {
                    "startDate": (now).isoformat(),
                }
            })
        elif status == 'active.pre-qualification.stand-still':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now - TENDERING_DURATION).isoformat(),
                    "endDate": (now - QUESTIONS_STAND_STILL).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - TENDERING_DURATION).isoformat(),
                    "endDate": (now).isoformat(),
                },
                "qualificationPeriod": {
                    "startDate": (now).isoformat(),
                },
                "auctionPeriod": {
                    "startDate": (now + COMPLAINT_STAND_STILL).isoformat()
                }
            })
        elif status == 'active.auction':
            data.update({
                "enquiryPeriod": {
                    "startDate": (now - TENDERING_DURATION - COMPLAINT_STAND_STILL).isoformat(),
                    "endDate": (now - COMPLAINT_STAND_STILL - TENDERING_DURATION + QUESTIONS_STAND_STILL).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - TENDERING_DURATION - COMPLAINT_STAND_STILL).isoformat(),
                    "endDate": (now - COMPLAINT_STAND_STILL).isoformat()
                },
                "qualificationPeriod": {
                    "startDate": (now - COMPLAINT_STAND_STILL).isoformat(),
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
                    "startDate": (now - TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=1)).isoformat(),
                    "endDate": (now - QUESTIONS_STAND_STILL - COMPLAINT_STAND_STILL - timedelta(days=1)).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=1)).isoformat(),
                    "endDate": (now - COMPLAINT_STAND_STILL - timedelta(days=1)).isoformat()
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
                    "startDate": (now - TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=2)).isoformat(),
                    "endDate": (now - TENDERING_DURATION + QUESTIONS_STAND_STILL - COMPLAINT_STAND_STILL - timedelta(days=2)).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=2)).isoformat(),
                    "endDate": (now - TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=2)).isoformat()
                },
                "auctionPeriod": {
                    "startDate": (now - timedelta(days=2)).isoformat(),
                    "endDate": (now - timedelta(days=1)).isoformat()
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
                    "startDate": (now - TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=3)).isoformat(),
                    "endDate": (now - TENDERING_DURATION + QUESTIONS_STAND_STILL - COMPLAINT_STAND_STILL - timedelta(days=3)).isoformat()
                },
                "tenderPeriod": {
                    "startDate": (now - TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=3)).isoformat(),
                    "endDate": (now - TENDERING_DURATION - COMPLAINT_STAND_STILL - timedelta(days=3)).isoformat()
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


class BaseTenderContentWebTest(BaseTenderWebTest):
    initial_data = test_tender_data
    initial_status = None
    initial_bids = None
    initial_lots = None

    def setUp(self):
        super(BaseTenderContentWebTest, self).setUp()
        self.create_tender()
