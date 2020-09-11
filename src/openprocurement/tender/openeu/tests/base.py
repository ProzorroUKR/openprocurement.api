# -*- coding: utf-8 -*-
import copy
import os

from datetime import datetime, timedelta
from openprocurement.api.constants import SANDBOX_MODE, RELEASE_ECRITERIA_ARTICLE_17
from openprocurement.tender.belowthreshold.tests.base import test_milestones as base_test_milestones
from openprocurement.tender.openeu.models import Tender
from openprocurement.tender.openeu.tests.periods import PERIODS
from openprocurement.tender.openua.tests.base import BaseTenderUAWebTest
from openprocurement.api.utils import get_now
from openprocurement.tender.openeu.constants import (
    TENDERING_DAYS,
)

test_milestones = copy.deepcopy(base_test_milestones)

test_bids = [
    {
        "tenderers": [
            {
                "name": u"Державне управління справами",
                "name_en": u"State administration",
                "identifier": {
                    "legalName_en": u"dus.gov.ua",
                    "legalName": u"Державне управління справами",
                    "scheme": u"UA-EDR",
                    "id": u"00037256",
                    "uri": u"http://www.dus.gov.ua/",
                },
                "address": {
                    "countryName": u"Україна",
                    "postalCode": u"01220",
                    "region": u"м. Київ",
                    "locality": u"м. Київ",
                    "streetAddress": u"вул. Банкова, 11, корпус 1",
                },
                "contactPoint": {
                    "name": u"Державне управління справами",
                    "name_en": u"State administration",
                    "telephone": u"0440000000",
                },
                "scale": "micro",
            }
        ],
        "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
        "selfQualified": True,
    },
    {
        "tenderers": [
            {
                "name": u"Державне управління справами",
                "name_en": u"State administration",
                "identifier": {
                    "legalName_en": u"dus.gov.ua",
                    "legalName": u"Державне управління справами",
                    "scheme": u"UA-EDR",
                    "id": u"00037256",
                    "uri": u"http://www.dus.gov.ua/",
                },
                "address": {
                    "countryName": u"Україна",
                    "postalCode": u"01220",
                    "region": u"м. Київ",
                    "locality": u"м. Київ",
                    "streetAddress": u"вул. Банкова, 11, корпус 1",
                },
                "contactPoint": {
                    "name": u"Державне управління справами",
                    "name_en": u"State administration",
                    "telephone": u"0440000000",
                },
                "scale": "micro",
            }
        ],
        "value": {"amount": 479, "currency": "UAH", "valueAddedTaxIncluded": True},
        "selfQualified": True,
    },
]

if get_now() < RELEASE_ECRITERIA_ARTICLE_17:
    for i in test_bids:
        i["selfEligible"] = True

now = datetime.now()
test_tender_data = {
    "title": u"футляри до державних нагород",
    "title_en": u"Cases for state awards",
    "mainProcurementCategory": "services",
    "procuringEntity": {
        "kind": "general",
        "name": u"Державне управління справами",
        "name_en": u"State administration",
        "identifier": {
            "legalName_en": u"dus.gov.ua",
            "scheme": u"UA-EDR",
            "id": u"00037256",
            "uri": u"http://www.dus.gov.ua/",
        },
        "address": {
            "countryName": u"Україна",
            "postalCode": u"01220",
            "region": u"м. Київ",
            "locality": u"м. Київ",
            "streetAddress": u"вул. Банкова, 11, корпус 1",
        },
        "contactPoint": {
            "name": u"Державне управління справами",
            "name_en": u"State administration",
            "telephone": u"0440000000",
        },
    },
    "value": {"amount": 500, "currency": u"UAH"},
    "minimalStep": {"amount": 15, "currency": u"UAH"},
    "items": [
        {
            "description": u"футляри до державних нагород",
            "description_en": u"Cases for state awards",
            "classification": {"scheme": u"ДК021", "id": u"44617100-9", "description": u"Cartons"},
            "additionalClassifications": [
                {
                    "scheme": u"ДКПП",
                    "id": u"17.21.1",
                    "description": u"папір і картон гофровані, паперова й картонна тара",
                }
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
    ],
    "tenderPeriod": {"endDate": (now + timedelta(days=TENDERING_DAYS + 1)).isoformat()},
    "procurementMethodType": "aboveThresholdEU",
    "milestones": test_milestones,
}
if SANDBOX_MODE:
    test_tender_data["procurementMethodDetails"] = "quick, accelerator=1440"

test_features_tender_data = test_tender_data.copy()
test_features_item = test_features_tender_data["items"][0].copy()
test_features_item["id"] = "1"
test_features_tender_data["items"] = [test_features_item]
test_features_tender_data["features"] = [
    {
        "code": "OCDS-123454-AIR-INTAKE",
        "featureOf": "item",
        "relatedItem": "1",
        "title": u"Потужність всмоктування",
        "title_en": "Air Intake",
        "description": u"Ефективна потужність всмоктування пилососа, в ватах (аероватах)",
        "enum": [{"value": 0.1, "title": u"До 1000 Вт"}, {"value": 0.15, "title": u"Більше 1000 Вт"}],
    },
    {
        "code": "OCDS-123454-YEARS",
        "featureOf": "tenderer",
        "title": u"Років на ринку",
        "title_en": "Years trading",
        "description": u"Кількість років, які організація учасник працює на ринку",
        "enum": [
            {"value": 0.05, "title": u"До 3 років"},
            {"value": 0.1, "title": u"Більше 3 років, менше 5 років"},
            {"value": 0.15, "title": u"Більше 5 років"},
        ],
    },
]

test_lots = [
    {
        "title": "lot title",
        "description": "lot description",
        "value": test_tender_data["value"],
        "minimalStep": test_tender_data["minimalStep"],
    }
]


class BaseTenderWebTest(BaseTenderUAWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_data
    initial_status = None
    initial_bids = None
    initial_lots = None
    initial_auth = None
    forbidden_question_modification_actions_status = (
        "active.pre-qualification"
    )  # status, in which adding/updating tender questions is forbidden
    question_claim_block_status = (
        "active.pre-qualification"
    )  # status, tender cannot be switched to while it has questions/complaints related to its lot
    # auction role actions
    forbidden_auction_actions_status = (
        "active.pre-qualification.stand-still"
    )  # status, in which operations with tender auction (getting auction info, reporting auction results, updating auction urls) and adding tender documents are forbidden
    forbidden_auction_document_create_actions_status = (
        "active.pre-qualification.stand-still"
    )  # status, in which adding document to tender auction is forbidden

    periods = PERIODS
    tender_class = Tender

    def set_enquiry_period_end(self):
        self.set_status("active.tendering", startend="enquiry_end")

    def set_complaint_period_end(self):
        self.set_status("active.tendering", startend="complaint_end")

    def setUp(self):
        super(BaseTenderUAWebTest, self).setUp()
        self.app.authorization = self.initial_auth or ("Basic", ("token", ""))

    def set_status(self, status, extra=None, startend="start"):
        self.now = get_now()
        self.tender_document = self.db.get(self.tender_id)
        self.tender_document_patch = {"status": status}
        self.update_periods(status, startend=startend)

        def activate_bids():
            if self.tender_document.get("bids", ""):
                bids = self.tender_document["bids"]
                for bid in bids:
                    if bid["status"] == "pending":
                        bid.update({"status": "active"})
                self.tender_document_patch.update({"bids": bids})

        data = {"status": status}
        if status == "active.pre-qualification.stand-still":
            activate_bids()
        elif status == "active.auction":
            activate_bids()
        elif status == "active.qualification":
            activate_bids()
        elif status == "active.awarded":
            activate_bids()

        if extra:
            self.tender_document_patch.update(extra)

        self.save_changes()
        return self.get_tender("chronograph")

    def prepare_award(self):
        # switch to active.pre-qualification
        self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
        self.app.authorization = ("Basic", ("chronograph", ""))
        response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

        # qualify bids
        response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
        self.app.authorization = ("Basic", ("broker", ""))
        for qualification in response.json["data"]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(
                    self.tender_id, qualification["id"], self.tender_token
                ),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"status": "active.pre-qualification.stand-still"}},
        )
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

        # switch to active.auction
        self.set_status("active.auction", {"id": self.tender_id, "status": "active.pre-qualification.stand-still"})
        self.app.authorization = ("Basic", ("chronograph", ""))
        response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json["data"]["status"], "active.auction")

        self.app.authorization = ("Basic", ("auction", ""))
        response = self.app.get("/tenders/{}/auction".format(self.tender_id))
        auction_bids_data = response.json["data"]["bids"]
        for lot_id in self.initial_lots:
            response = self.app.post_json(
                "/tenders/{}/auction/{}".format(self.tender_id, lot_id["id"]), {"data": {"bids": auction_bids_data}}
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
        response = self.app.get("/tenders/{}".format(self.tender_id))
        self.assertEqual(response.json["data"]["status"], "active.qualification")


class BaseTenderContentWebTest(BaseTenderWebTest):
    initial_data = test_tender_data
    initial_status = None
    initial_bids = None
    initial_lots = None

    def setUp(self):
        super(BaseTenderContentWebTest, self).setUp()
        self.create_tender()
