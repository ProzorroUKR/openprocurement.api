# -*- coding: utf-8 -*-
import copy
import os

from datetime import datetime, timedelta
from openprocurement.api.constants import SANDBOX_MODE, RELEASE_ECRITERIA_ARTICLE_17
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_milestones,
    test_tender_below_organization,
)
from openprocurement.tender.belowthreshold.tests.utils import set_tender_multi_buyers
from openprocurement.tender.openeu.models import Tender
from openprocurement.tender.openeu.tests.periods import PERIODS
from openprocurement.tender.openua.tests.base import BaseTenderUAWebTest
from openprocurement.api.utils import get_now
from openprocurement.tender.openeu.constants import TENDERING_DAYS


test_tender_openeu_milestones = copy.deepcopy(test_tender_below_milestones)

test_tender_openeu_bids = [
    {
        "tenderers": [
            {
                "name": "Державне управління справами",
                "name_en": "State administration",
                "identifier": {
                    "legalName_en": "dus.gov.ua",
                    "legalName": "Державне управління справами",
                    "scheme": "UA-EDR",
                    "id": "00037256",
                    "uri": "http://www.dus.gov.ua/",
                },
                "address": {
                    "countryName": "Україна",
                    "postalCode": "01220",
                    "region": "м. Київ",
                    "locality": "м. Київ",
                    "streetAddress": "вул. Банкова, 11, корпус 1",
                },
                "contactPoint": {
                    "name": "Державне управління справами",
                    "name_en": "State administration",
                    "telephone": "+0440000000",
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
                "name": "Державне управління справами",
                "name_en": "State administration",
                "identifier": {
                    "legalName_en": "dus.gov.ua",
                    "legalName": "Державне управління справами",
                    "scheme": "UA-EDR",
                    "id": "00037256",
                    "uri": "http://www.dus.gov.ua/",
                },
                "address": {
                    "countryName": "Україна",
                    "postalCode": "01220",
                    "region": "м. Київ",
                    "locality": "м. Київ",
                    "streetAddress": "вул. Банкова, 11, корпус 1",
                },
                "contactPoint": {
                    "name": "Державне управління справами",
                    "name_en": "State administration",
                    "telephone": "+0440000000",
                },
                "scale": "micro",
            }
        ],
        "value": {"amount": 479, "currency": "UAH", "valueAddedTaxIncluded": True},
        "selfQualified": True,
    },
]

for bid in test_tender_openeu_bids:
    if get_now() < RELEASE_ECRITERIA_ARTICLE_17:
        bid["selfEligible"] = True

now = datetime.now()

test_tender_openeu_data = {
    "title": "футляри до державних нагород",
    "title_en": "Cases for state awards",
    "mainProcurementCategory": "services",
    "procuringEntity": {
        "kind": "general",
        "name": "Державне управління справами",
        "name_en": "State administration",
        "identifier": {
            "legalName_en": "dus.gov.ua",
            "scheme": "UA-EDR",
            "id": "00037256",
            "uri": "http://www.dus.gov.ua/",
        },
        "address": {
            "countryName": "Україна",
            "postalCode": "01220",
            "region": "м. Київ",
            "locality": "м. Київ",
            "streetAddress": "вул. Банкова, 11, корпус 1",
        },
        "contactPoint": {
            "name": "Державне управління справами",
            "name_en": "State administration",
            "telephone": "+0440000000",
        },
    },
    "value": {"amount": 500, "currency": "UAH"},
    "minimalStep": {"amount": 15, "currency": "UAH"},
    "items": [
        {
            "description": "футляри до державних нагород",
            "description_en": "Cases for state awards",
            "classification": {"scheme": "ДК021", "id": "44617100-9", "description": "Cartons"},
            "additionalClassifications": [
                {
                    "scheme": "ДКПП",
                    "id": "17.21.1",
                    "description": "папір і картон гофровані, паперова й картонна тара",
                }
            ],
            "unit": {
                "name": "item",
                "code": "KGM",
                "value": {"amount": 6}
            },
            "quantity": 5,
            "deliveryDate": {
                "startDate": (now + timedelta(days=2)).isoformat(),
                "endDate": (now + timedelta(days=5)).isoformat(),
            },
            "deliveryAddress": {
                "countryName": "Україна",
                "postalCode": "79000",
                "region": "м. Київ",
                "locality": "м. Київ",
                "streetAddress": "вул. Банкова 1",
            },
        }
    ],
    "tenderPeriod": {"endDate": (now + timedelta(days=TENDERING_DAYS + 1)).isoformat()},
    "procurementMethodType": "aboveThresholdEU",
    "milestones": test_tender_openeu_milestones,
}
if SANDBOX_MODE:
    test_tender_openeu_data["procurementMethodDetails"] = "quick, accelerator=1440"

test_tender_openeu_features_data = test_tender_openeu_data.copy()
test_tender_openeu_features_item = test_tender_openeu_features_data["items"][0].copy()
test_tender_openeu_features_item["id"] = "1"
test_tender_openeu_features_data["items"] = [test_tender_openeu_features_item]
test_tender_openeu_features_data["features"] = [
    {
        "code": "OCDS-123454-AIR-INTAKE",
        "featureOf": "item",
        "relatedItem": "1",
        "title": "Потужність всмоктування",
        "title_en": "Air Intake",
        "description": "Ефективна потужність всмоктування пилососа, в ватах (аероватах)",
        "enum": [{"value": 0.1, "title": "До 1000 Вт"}, {"value": 0.15, "title": "Більше 1000 Вт"}],
    },
    {
        "code": "OCDS-123454-YEARS",
        "featureOf": "tenderer",
        "title": "Років на ринку",
        "title_en": "Years trading",
        "description": "Кількість років, які організація учасник працює на ринку",
        "enum": [
            {"value": 0.05, "title": "До 3 років"},
            {"value": 0.1, "title": "Більше 3 років, менше 5 років"},
            {"value": 0.15, "title": "Більше 5 років"},
        ],
    },
]

test_tender_openeu_lots = [
    {
        "title": "lot title",
        "description": "lot description",
        "value": test_tender_openeu_data["value"],
        "minimalStep": test_tender_openeu_data["minimalStep"],
    }
]

test_tender_openeu_multi_buyers_data = set_tender_multi_buyers(
    test_tender_openeu_data,
    test_tender_openeu_data["items"][0],
    test_tender_below_organization
)

test_tender_openeu_restricted_data = test_tender_openeu_features_data.copy()
test_tender_openeu_restricted_data.update({
    "preQualificationFeaturesRatingBidLimit": 5,
    "preQualificationMinBidsNumber": 4
})

test_tender_openeu_restricted_bids = test_tender_openeu_bids

test_tender_openeu_config = {
    "hasAuction": True,
}

class BaseTenderWebTest(BaseTenderUAWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_openeu_data
    initial_config = test_tender_openeu_config
    initial_status = "active.tendering"
    initial_bids = None
    initial_lots = None
    initial_auth = None
    forbidden_question_add_actions_status = (
        "active.pre-qualification"
    )  # status, in which adding tender questions is forbidden
    forbidden_question_update_actions_status = (
        "active.pre-qualification"
    )  # status, in which updating tender questions is forbidden
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
        self.tender_document = self.mongodb.tenders.get(self.tender_id)
        old_status = self.tender_document["status"]
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
        if old_status == "draft" and status == "active.tendering" and startend == "start":
            self.app.patch_json(
                f"/tenders/{self.tender_document['_id']}?acc_token={self.tender_document['owner_token']}",
                {"data": {}}
            )
        return self.get_tender("chronograph")

    def prepare_award(self):
        # switch to active.pre-qualification
        self.set_status("active.pre-qualification", {"id": self.tender_id, "status": "active.tendering"})
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

        # qualify bids
        response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
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
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.auction")

        with change_auth(self.app, ("Basic", ("auction", ""))):
            response = self.app.get("/tenders/{}/auction".format(self.tender_id))
            auction_bids_data = response.json["data"]["bids"]
            for lot_id in self.initial_lots:
                response = self.app.post_json(
                    "/tenders/{}/auction/{}".format(self.tender_id, lot_id["id"]),
                    {"data": {"bids": [
                        {"id": b["id"],
                         "lotValues": [
                             {"relatedLot": l["relatedLot"],
                              "value": {
                                  "yearlyPaymentsPercentage": l["value"]["yearlyPaymentsPercentage"],
                                  "contractDuration": l["value"]["contractDuration"]
                              } if "contractDuration" in l["value"] else {
                                  "amount": l["value"]["amount"]}
                              } for l in b["lotValues"]]}
                        for b in auction_bids_data]}}
                )
                self.assertEqual(response.status, "200 OK")
                self.assertEqual(response.content_type, "application/json")
        response = self.app.get("/tenders/{}".format(self.tender_id))
        self.assertEqual(response.json["data"]["status"], "active.qualification")


class BaseTenderContentWebTest(BaseTenderWebTest):
    initial_status = "active.tendering"
    initial_bids = None
    initial_lots = None

    def setUp(self):
        super(BaseTenderContentWebTest, self).setUp()
        self.create_tender()
