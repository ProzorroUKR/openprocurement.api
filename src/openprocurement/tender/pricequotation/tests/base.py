# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from uuid import uuid4

from datetime import timedelta

from openprocurement.api.constants import SANDBOX_MODE, RELEASE_2020_04_19
from openprocurement.api.tests.base import BaseWebTest
from openprocurement.api.utils import get_now
from openprocurement.tender.core.tests.base import BaseCoreWebTest
from openprocurement.tender.belowthreshold.constants import MIN_BIDS_NUMBER
from openprocurement.tender.pricequotation.constants import PMT


now = get_now()
test_organization = {
    "name": u"Державне управління справами",
    "identifier": {"scheme": u"UA-EDR", "id": u"00037256", "uri": u"http://www.dus.gov.ua/"},
    "address": {
        "countryName": u"Україна",
        "postalCode": u"01220",
        "region": u"м. Київ",
        "locality": u"м. Київ",
        "streetAddress": u"вул. Банкова, 11, корпус 1",
    },
    "contactPoint": {"name": u"Державне управління справами", "telephone": u"0440000000"},
    "scale": "micro",
}

test_author = test_organization.copy()
del test_author["scale"]

test_procuringEntity = test_author.copy()
test_procuringEntity["kind"] = "general"
test_milestones = [
    {
        "id": "a" * 32,
        "title": "signingTheContract",
        "code": "prepayment",
        "type": "financing",
        "duration": {"days": 2, "type": "banking"},
        "sequenceNumber": 0,
        "percentage": 45.55,
    },
    {
        "title": "deliveryOfGoods",
        "code": "postpayment",
        "type": "financing",
        "duration": {"days": 900, "type": "calendar"},
        "sequenceNumber": 0,
        "percentage": 54.45,
    },
]

test_item = {
    "description": u"Комп’ютерне обладнання",
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

test_tender_data = {
    "title": u"Комп’ютерне обладнання",
    "mainProcurementCategory": "goods",
    "procuringEntity": test_procuringEntity,
    "value": {"amount": 500, "currency": u"UAH"},
    "minimalStep": {"amount": 35, "currency": u"UAH"},
    "items": [deepcopy(test_item)],
    "tenderPeriod": {"endDate": (now + timedelta(days=14)).isoformat()},
    "procurementMethodType": PMT,
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
test_bids = [
    {"tenderers": [test_organization], "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True}},
    {"tenderers": [test_organization], "value": {"amount": 479, "currency": "UAH", "valueAddedTaxIncluded": True}},
]
test_lots = [
    {
        "title": "lot title",
        "description": "lot description",
        "value": test_tender_data["value"],
        "minimalStep": test_tender_data["minimalStep"],
    }
]
test_features = [
    {
        "code": "code_item",
        "featureOf": "item",
        "relatedItem": "1",
        "title": u"item feature",
        "enum": [{"value": 0.01, "title": u"good"}, {"value": 0.02, "title": u"best"}],
    },
    {
        "code": "code_tenderer",
        "featureOf": "tenderer",
        "title": u"tenderer feature",
        "enum": [{"value": 0.01, "title": u"good"}, {"value": 0.02, "title": u"best"}],
    },
]
test_cancellation = {
    "reason": "cancellation reason",
}
if RELEASE_2020_04_19 < get_now():
    test_cancellation.update({
        "reasonType": "noDemand"
    })

test_draft_claim = {
    "title": "complaint title",
    "status": "draft",
    "type": "claim",
    "description": "complaint description",
    "author": test_author
}

test_claim = {
    "title": "complaint title",
    "status": "claim",
    "type": "claim",
    "description": "complaint description",
    "author": test_author
}

test_complaint = {
    "title": "complaint title",
    "status": "pending",
    "type": "complaint",
    "description": "complaint description",
    "author": test_author
}
test_draft_complaint = {
    "title": "complaint title",
    "type": "complaint",
    "description": "complaint description",
    "author": test_author
}

test_shortlisted_firms = [
    {
        "address": {
            "countryName": "Україна",
            "locality": "м.Київ",
            "postalCode": "01100",
            "region": "Київська область",
            "streetAddress": "бул.Дружби Народів, 8"
        },
        "contactPoint": {
            "email": "contact@pixel.pix",
            "name": "Оксана Піксель",
            "telephone": "(067) 123-45-67"
        },
        "id": "UA-EDR-12345678",
        "identifier": {
            "id": "12345678",
            "legalName": "Товариство з обмеженою відповідальністю «Пікселі»",
            "scheme": "UA-EDR"
        },
        "name": "Товариство з обмеженою відповідальністю «Пікселі»",
        "scale": "large",
        "status": "active"
    },
    {
        "address": {
            "countryName": "Україна",
            "locality": "м.Тернопіль",
            "postalCode": "46000",
            "region": "Тернопільська область",
            "streetAddress": "вул. Кластерна, 777-К"
        },
        "contactPoint": {
            "email": "info@shteker.pek",
            "name": "Олег Штекер",
            "telephone": "(095) 123-45-67"
        },
        "id": "UA-EDR-87654321",
        "identifier": {
            "id": "87654321",
            "legalName": "Товариство з обмеженою відповідальністю «Штекер-Пекер»",
            "scheme": "UA-EDR"
        },
        "name": "Товариство з обмеженою відповідальністю «Штекер-Пекер»",
        "scale": "large",
        "status": "active"
    }
]

test_short_profile = {
    "classification": {
        "description": "Комп’ютерне обладнанн",
        "id": "30230000-0",
        "scheme": "ДК021"
    },
    "id": "655360-30230000-889652-40000777",
    "unit": {
        "code": "H87",
        "name": "штук"
    }
}


def set_tender_lots(tender, lots):
    tender["lots"] = []
    for lot in lots:
        lot = deepcopy(lot)
        lot["id"] = uuid4().hex
        tender["lots"].append(lot)
    for i, item in enumerate(tender["items"]):
        item["relatedLot"] = tender["lots"][i % len(tender["lots"])]["id"]
    return tender


def set_bid_lotvalues(bid, lots):
    value = bid.pop("value", None) or bid["lotValues"][0]["value"]
    bid["lotValues"] = [{"value": value, "relatedLot": lot["id"]} for lot in lots]
    return bid


class BaseApiWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)


class BaseTenderWebTest(BaseCoreWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_data
    initial_status = None
    initial_bids = None
    initial_lots = None
    initial_auth = ("Basic", ("broker", ""))
    docservice = False
    min_bids_number = MIN_BIDS_NUMBER
    # Statuses for test, that will be imported from others procedures
    primary_tender_status = "draft.publishing"  # status, to which tender should be switched from 'draft'
    forbidden_document_modification_actions_status = (
        "active.tendering"
    )  # status, in which operations with tender documents (adding, updating) are forbidden
    forbidden_question_modification_actions_status = (
        "active.tendering"
    )  # status, in which adding/updating tender questions is forbidden
    forbidden_lot_actions_status = (
        "active.tendering"
    )  # status, in which operations with tender lots (adding, updating, deleting) are forbidden
    forbidden_contract_document_modification_actions_status = (
        "unsuccessful"
    )  # status, in which operations with tender's contract documents (adding, updating) are forbidden
    # auction role actions
    forbidden_auction_actions_status = (
        "active.tendering"
    )  # status, in which operations with tender auction (getting auction info, reporting auction results, updating auction urls) and adding tender documents are forbidden
    forbidden_auction_document_create_actions_status = (
        "active.tendering"
    )  # status, in which adding document to tender auction is forbidden

    def update_status(self, status, extra=None):
        now = get_now()
        data = {"status": status}
        if status == "active.tendering":
            items = deepcopy(self.initial_data["items"])
            for item in items:
                item.update({"classification": test_short_profile["classification"],
                             "unit": test_short_profile["unit"]})
            data.update(
                {
                    "tenderPeriod": {"startDate": (now).isoformat(), "endDate": (now + timedelta(days=1)).isoformat()},
                    "shortlistedFirms": test_shortlisted_firms,
                    "items": items
                }
            )
        elif status == "active.qualification":
            data.update(
                {
                    "tenderPeriod": {
                        "startDate": (now - timedelta(days=8)).isoformat(),
                        "endDate": (now - timedelta(days=1)).isoformat(),
                    },
                    "awardPeriod": {"startDate": (now).isoformat()},
                }
            )
        elif status == "active.awarded":
            data.update(
                {
                    "tenderPeriod": {
                        "startDate": (now - timedelta(days=8)).isoformat(),
                        "endDate": (now - timedelta(days=1)).isoformat(),
                    },
                    "awardPeriod": {"startDate": (now).isoformat(), "endDate": (now).isoformat()},
                }
            )
        elif status == "complete":
            data.update(
                {
                    "tenderPeriod": {
                        "startDate": (now - timedelta(days=18)).isoformat(),
                        "endDate": (now - timedelta(days=11)).isoformat(),
                    },
                    "awardPeriod": {
                        "startDate": (now - timedelta(days=10)).isoformat(),
                        "endDate": (now - timedelta(days=10)).isoformat(),
                    },
                }
            )

        self.tender_document_patch = data
        if extra:
            self.tender_document_patch.update(extra)
        self.save_changes()

    def create_tender(self):
        data = deepcopy(self.initial_data)
        if self.initial_lots:
            set_tender_lots(data, self.initial_lots)
            self.initial_lots = data["lots"]
        response = self.app.post_json("/tenders", {"data": data})
        tender = response.json["data"]
        self.tender_token = response.json["access"]["token"]
        self.tender_id = tender["id"]
        status = tender["status"]
        if self.initial_bids:
            self.initial_bids_tokens = {}
            response = self.set_status("active.tendering")
            status = response.json["data"]["status"]
            bids = []
            for bid in self.initial_bids:
                if self.initial_lots:
                    bid = bid.copy()
                    set_bid_lotvalues(bid, self.initial_lots)
                response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid})
                self.assertEqual(response.status, "201 Created")
                bids.append(response.json["data"])
                self.initial_bids_tokens[response.json["data"]["id"]] = response.json["access"]["token"]
            self.initial_bids = bids
        if self.initial_status and self.initial_status != status:
            self.set_status(self.initial_status)


class TenderContentWebTest(BaseTenderWebTest):
    initial_data = test_tender_data
    initial_status = None
    initial_bids = None
    initial_lots = None

    def setUp(self):
        super(TenderContentWebTest, self).setUp()
        self.create_tender()
