# -*- coding: utf-8 -*-
import os
from datetime import timedelta

from openprocurement.api.tests.base import BaseWebTest
from openprocurement.api.utils import get_now, apply_data_patch
from openprocurement.api.constants import SANDBOX_MODE
from openprocurement.tender.openua.tests.base import (
    now,
    test_features_tender_data,
    BaseTenderUAWebTest as BaseTenderWebTest,
)
from openprocurement.tender.belowthreshold.tests.base import (
    test_procuringEntity as test_procuringEntity_api,
    test_tender_data as test_tender_data_api,
)
from openprocurement.api.utils import apply_data_patch


test_tender_data = test_tender_ua_data = test_tender_data_api.copy()
test_tender_data["procurementMethodType"] = "aboveThresholdUA.defense"
test_procuringEntity = test_procuringEntity_api.copy()
test_procuringEntity["kind"] = "defense"
test_contactPoint = test_procuringEntity_api["contactPoint"].copy()
test_contactPoint["availableLanguage"] = "uk"
test_procuringEntity["contactPoint"] = test_contactPoint
test_procuringEntity["additionalContactPoints"] = [test_contactPoint.copy()]
test_tender_data["procuringEntity"] = test_procuringEntity
del test_tender_data["enquiryPeriod"]
test_tender_data["tenderPeriod"] = {"endDate": (now + timedelta(days=16)).isoformat()}
test_tender_data["items"] = [
    {
        "description": u"футляри до державних нагород",
        "description_en": u"Cases for state awards",
        "classification": {"scheme": u"ДК021", "id": u"44617100-9", "description": u"Cartons"},
        "additionalClassifications": [
            {"scheme": u"ДКПП", "id": u"17.21.1", "description": u"папір і картон гофровані, паперова й картонна тара"}
        ],
        "unit": {"name": u"item", "code": u"44617100-9"},
        "quantity": 5,
        "deliveryDate": {
            "startDate": (now + timedelta(days=2)).isoformat(),
            "endDate": (now + timedelta(days=5)).isoformat(),
        },
        "deliveryAddress": {
            "countryName": u"Україна",
            "postalCode": "79000",
            "region": u"м. Київ",
            "locality": u"м. Київ",
            "streetAddress": u"вул. Банкова 1",
        },
    }
]
if SANDBOX_MODE:
    test_tender_data["procurementMethodDetails"] = "quick, accelerator=1440"
test_features_tender_ua_data = test_features_tender_data.copy()
test_features_tender_ua_data["procurementMethodType"] = "aboveThresholdUA.defense"
test_features_tender_ua_data["procuringEntity"] = test_procuringEntity
del test_features_tender_ua_data["enquiryPeriod"]
test_features_tender_ua_data["tenderPeriod"] = {"endDate": (now + timedelta(days=16)).isoformat()}
test_features_tender_ua_data["items"][0]["deliveryDate"] = test_tender_data["items"][0]["deliveryDate"]
test_features_tender_ua_data["items"][0]["deliveryAddress"] = test_tender_data["items"][0]["deliveryAddress"]


class BaseApiWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)


class BaseTenderUAWebTest(BaseTenderWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_data
    initial_status = None
    initial_bids = None
    initial_lots = None
    forbidden_lot_actions_status = (
        "active.auction"
    )  # status, in which operations with tender lots (adding, updating, deleting) are forbidden

    def set_enquiry_period_end(self):
        now = get_now()
        self.set_status(
            "active.tendering",
            {
                "enquiryPeriod": {
                    "startDate": (now - timedelta(days=13)).isoformat(),
                    "endDate": (now - (timedelta(minutes=1) if SANDBOX_MODE else timedelta(days=1))).isoformat(),
                },
                "tenderPeriod": {
                    "startDate": (now - timedelta(days=13)).isoformat(),
                    "endDate": (now + (timedelta(minutes=2) if SANDBOX_MODE else timedelta(days=2))).isoformat(),
                },
                "auctionPeriod": {"startDate": (now + timedelta(days=2)).isoformat()},
            },
        )

    def set_complaint_period_end(self):
        now = get_now()
        self.set_status(
            "active.tendering",
            {
                "enquiryPeriod": {
                    "startDate": (now - timedelta(days=12)).isoformat(),
                    "endDate": now.isoformat(),
                },
                "tenderPeriod": {
                    "startDate": (now - timedelta(days=12)).isoformat(),
                    "endDate": (now + (timedelta(minutes=1) if SANDBOX_MODE else timedelta(days=1))).isoformat(),
                },
                "auctionPeriod": {"startDate": (now + timedelta(days=2)).isoformat()},
            },
        )

    def update_status(self, status, extra=None):
        now = get_now()
        data = {"status": status}
        if status == "active.tendering":
            data.update(
                {
                    "enquiryPeriod": {
                        "startDate": (now).isoformat(),
                        "endDate": (now + timedelta(days=13)).isoformat(),
                    },
                    "tenderPeriod": {"startDate": (now).isoformat(), "endDate": (now + timedelta(days=16)).isoformat()},
                }
            )
        elif status == "active.auction":
            data.update(
                {
                    "enquiryPeriod": {
                        "startDate": (now - timedelta(days=16)).isoformat(),
                        "endDate": (now - timedelta(days=3)).isoformat(),
                    },
                    "tenderPeriod": {"startDate": (now - timedelta(days=16)).isoformat(), "endDate": (now).isoformat()},
                    "auctionPeriod": {"startDate": (now).isoformat()},
                }
            )
            if self.initial_lots:
                data.update({"lots": [{"auctionPeriod": {"startDate": (now).isoformat()}} for i in self.initial_lots]})
        elif status == "active.qualification":
            data.update(
                {
                    "enquiryPeriod": {
                        "startDate": (now - timedelta(days=17)).isoformat(),
                        "endDate": (now - timedelta(days=4)).isoformat(),
                    },
                    "tenderPeriod": {
                        "startDate": (now - timedelta(days=17)).isoformat(),
                        "endDate": (now - timedelta(days=1)).isoformat(),
                    },
                    "auctionPeriod": {"startDate": (now - timedelta(days=1)).isoformat(), "endDate": (now).isoformat()},
                    "awardPeriod": {"startDate": (now).isoformat()},
                }
            )
            if self.initial_lots:
                data.update(
                    {
                        "lots": [
                            {
                                "auctionPeriod": {
                                    "startDate": (now - timedelta(days=1)).isoformat(),
                                    "endDate": (now).isoformat(),
                                }
                            }
                            for i in self.initial_lots
                        ]
                    }
                )
        elif status == "active.awarded":
            data.update(
                {
                    "enquiryPeriod": {
                        "startDate": (now - timedelta(days=17)).isoformat(),
                        "endDate": (now - timedelta(days=4)).isoformat(),
                    },
                    "tenderPeriod": {
                        "startDate": (now - timedelta(days=17)).isoformat(),
                        "endDate": (now - timedelta(days=1)).isoformat(),
                    },
                    "auctionPeriod": {"startDate": (now - timedelta(days=1)).isoformat(), "endDate": (now).isoformat()},
                    "awardPeriod": {"startDate": (now).isoformat(), "endDate": (now).isoformat()},
                }
            )
            if self.initial_lots:
                data.update(
                    {
                        "lots": [
                            {
                                "auctionPeriod": {
                                    "startDate": (now - timedelta(days=1)).isoformat(),
                                    "endDate": (now).isoformat(),
                                }
                            }
                            for i in self.initial_lots
                        ]
                    }
                )
        elif status == "complete":
            data.update(
                {
                    "enquiryPeriod": {
                        "startDate": (now - timedelta(days=25)).isoformat(),
                        "endDate": (now - timedelta(days=11)).isoformat(),
                    },
                    "tenderPeriod": {
                        "startDate": (now - timedelta(days=25)).isoformat(),
                        "endDate": (now - timedelta(days=8)).isoformat(),
                    },
                    "auctionPeriod": {
                        "startDate": (now - timedelta(days=8)).isoformat(),
                        "endDate": (now - timedelta(days=7)).isoformat(),
                    },
                    "awardPeriod": {
                        "startDate": (now - timedelta(days=7)).isoformat(),
                        "endDate": (now - timedelta(days=7)).isoformat(),
                    },
                }
            )
            if self.initial_lots:
                data.update(
                    {
                        "lots": [
                            {
                                "auctionPeriod": {
                                    "startDate": (now - timedelta(days=8)).isoformat(),
                                    "endDate": (now - timedelta(days=7)).isoformat(),
                                }
                            }
                            for i in self.initial_lots
                        ]
                    }
                )

        self.tender_document_patch = data
        if extra:
            self.tender_document_patch.update(extra)
        self.save_changes()


class BaseTenderUAContentWebTest(BaseTenderUAWebTest):
    initial_data = test_tender_data
    initial_status = None
    initial_bids = None
    initial_lots = None

    def setUp(self):
        super(BaseTenderUAContentWebTest, self).setUp()
        self.create_tender()
