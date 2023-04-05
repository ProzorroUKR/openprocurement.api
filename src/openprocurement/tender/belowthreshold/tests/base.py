# -*- coding: utf-8 -*-
import os
import json
from copy import deepcopy
from uuid import uuid4

from datetime import timedelta

from openprocurement.api.constants import (
    SANDBOX_MODE,
    RELEASE_2020_04_19,
)
from openprocurement.api.tests.base import BaseWebTest
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.models import Tender
from openprocurement.tender.belowthreshold.tests.periods import PERIODS
from openprocurement.tender.core.tests.base import BaseCoreWebTest
from openprocurement.tender.belowthreshold.constants import MIN_BIDS_NUMBER

now = get_now()
test_identifier = {
    "scheme": "UA-EDR",
    "id": "00037256",
    "uri": "http://www.dus.gov.ua/",
    "legalName": "Державне управління справами",
}

test_organization = {
    "name": "Державне управління справами",
    "identifier": test_identifier,
    "address": {
        "countryName": "Україна",
        "postalCode": "01220",
        "region": "м. Київ",
        "locality": "м. Київ",
        "streetAddress": "вул. Банкова, 11, корпус 1",
    },
    "contactPoint": {
        "name": "Державне управління справами",
        "telephone": "+0440000000",
    },
    "scale": "micro",
}

test_author = test_organization.copy()
del test_author["scale"]

test_procuring_entity = test_author.copy()
test_procuring_entity["kind"] = "general"
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
    "description": "футляри до державних нагород",
    "classification": {"scheme": "ДК021", "id": "44617100-9", "description": "Cartons"},
    "additionalClassifications": [
        {"scheme": "ДКПП", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"}
    ],
    "unit": {
        "name": "кг",
        "code": "KGM",
        "value": {"amount": 6},
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

test_tender_data = {
    "title": "футляри до державних нагород",
    "mainProcurementCategory": "goods",
    "procuringEntity": test_procuring_entity,
    "value": {"amount": 500, "currency": "UAH"},
    "minimalStep": {"amount": 15, "currency": "UAH"},
    "items": [deepcopy(test_item)],
    "enquiryPeriod": {"endDate": (now + timedelta(days=9)).isoformat()},
    "tenderPeriod": {"endDate": (now + timedelta(days=18)).isoformat()},
    "procurementMethodType": "belowThreshold",
    "milestones": test_milestones,
}
if SANDBOX_MODE:
    test_tender_data["procurementMethodDetails"] = "quick, accelerator=1440"

test_tender_config = {
    "hasAuction": True,
}

test_simple_tender_data = deepcopy(test_tender_data)
test_simple_tender_data["procurementMethodRationale"] = "simple"

test_features_tender_data = test_tender_data.copy()
test_features_item = test_features_tender_data["items"][0].copy()
test_features_item["id"] = "1"
test_features_tender_data["items"] = [test_features_item]
test_features_tender_data["features"] = [
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
test_bids = [
    {"tenderers": [test_organization], "value": {"amount": 469.0, "currency": "UAH", "valueAddedTaxIncluded": True}},
    {"tenderers": [test_organization], "value": {"amount": 479.0, "currency": "UAH", "valueAddedTaxIncluded": True}},
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
        "title": "item feature",
        "enum": [{"value": 0.01, "title": "good"}, {"value": 0.02, "title": "best"}],
    },
    {
        "code": "code_tenderer",
        "featureOf": "tenderer",
        "title": "tenderer feature",
        "enum": [{"value": 0.01, "title": "good"}, {"value": 0.02, "title": "best"}],
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


current_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(current_dir, "data", "exclusion_criteria.json")) as json_file:
    test_criteria = json.load(json_file)

test_requirement_groups = test_criteria[0]["requirementGroups"]

with open(os.path.join(current_dir, "data", "lang_criteria.json")) as json_file:
    language_criteria = json.load(json_file)

with open(os.path.join(current_dir, "data", "contract_guarantee_criteria.json")) as json_file:
    contract_guarantee_criteria = json.load(json_file)

with open(os.path.join(current_dir, "data", "tender_guarantee_criteria.json")) as json_file:
    tender_guarantee_criteria = json.load(json_file)


def set_tender_lots(tender, lots):
    tender["lots"] = []
    for lot in lots:
        lot = deepcopy(lot)
        lot["id"] = uuid4().hex
        tender["lots"].append(lot)
    for i, item in enumerate(tender["items"]):
        item["relatedLot"] = tender["lots"][i % len(tender["lots"])]["id"]
    return tender


def set_tender_criteria(criteria, lots, items):
    for i, criterion in enumerate(criteria):
        if lots and criterion["relatesTo"] == "lot":
            criterion["relatedItem"] = lots[i % len(lots)]["id"]
        elif items and criterion["relatesTo"] == "item":
            criterion["relatedItem"] = items[i % len(lots)]["id"]
    return criteria


def set_bid_responses(criteria):
    rrs = []
    for criterion in criteria:
        for req in criterion["requirementGroups"][0]["requirements"]:
            if criterion["source"] == "tenderer":
                rrs.append(
                    {
                        "title": "Requirement response",
                        "description": "some description",
                        "requirement": {
                            "id": req["id"],
                            "title": req["title"],
                        },
                        "value": True,
                    },
                )
    return rrs


def set_bid_lotvalues(bid, lots):
    try:
        value = bid.pop("value", None) or bid["lotValues"][0]["value"]
    except KeyError:
        bid["lotValues"] = [{"relatedLot": lot["id"]} for lot in lots]
    else:
        bid["lotValues"] = [{"value": value, "relatedLot": lot["id"]} for lot in lots]
    return bid


def set_tender_multi_buyers(_test_tender_data, _test_item, _test_organization):
    _tender_data = deepcopy(_test_tender_data)

    # create 3 items
    test_item1 = deepcopy(_test_item)
    test_item1["description"] = "телевізори"

    test_item2 = deepcopy(_test_item)
    test_item2["description"] = "портфелі"
    test_item2.pop("id", None)

    test_item3 = deepcopy(_test_item)
    test_item3["description"] = "столи"
    test_item3.pop("id", None)

    _tender_data["items"] = [test_item1, test_item2, test_item2]

    # create 2 buyers
    buyer1_id = uuid4().hex
    buyer2_id = uuid4().hex

    _test_organization_1 = deepcopy(_test_organization)
    _test_organization_2 = deepcopy(_test_organization)
    _test_organization_2["identifier"]["id"] = "00037254"

    _tender_data["buyers"] = [
        {
            "id": buyer1_id,
            "name": _test_organization_1["name"],
            "identifier": _test_organization_1["identifier"]
        },
        {
            "id": buyer2_id,
            "name": _test_organization_2["name"],
            "identifier": _test_organization_2["identifier"]
        },
    ]
    # assign items to buyers
    _tender_data["items"][0]["relatedBuyer"] = buyer1_id
    _tender_data["items"][1]["relatedBuyer"] = buyer2_id
    _tender_data["items"][2]["relatedBuyer"] = buyer2_id

    return _tender_data


test_tender_data_multi_buyers = set_tender_multi_buyers(test_tender_data, test_item, test_organization)


class BaseApiWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)


class BaseTenderWebTest(BaseCoreWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_data
    initial_config = test_tender_config
    initial_status = "active.enquiries"
    initial_bids = None
    initial_lots = None
    initial_criteria = None
    initial_auth = ("Basic", ("broker", ""))
    docservice = True
    min_bids_number = MIN_BIDS_NUMBER
    # Statuses for test, that will be imported from others procedures
    primary_tender_status = "active.enquiries"  # status, to which tender should be switched from 'draft'
    forbidden_document_modification_actions_status = (
        "active.tendering"
    )  # status, in which operations with tender documents (adding, updating) are forbidden
    forbidden_question_add_actions_status = (
        "active.tendering"
    )  # status, in which adding tender questions is forbidden
    forbidden_question_update_actions_status = (
        "active.auction"
    )  # status, in which updating tender questions is forbidden
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

    periods = PERIODS
    tender_class = Tender
    guarantee_criterion = None

    def set_enquiry_period_end(self):
        self.set_status("active.tendering", extra={"status": "active.enquires"})

    def setUp(self):
        super(BaseTenderWebTest, self).setUp()
        self.initial_data = deepcopy(self.initial_data)
        self.initial_config = deepcopy(self.initial_config)
        if self.initial_lots:
            self.initial_lots = deepcopy(self.initial_lots)
            set_tender_lots(self.initial_data, self.initial_lots)
            self.initial_lots = self.initial_data["lots"]
        if self.initial_bids:
            self.initial_bids = deepcopy(self.initial_bids)
            for bid in self.initial_bids:
                if self.initial_lots:
                    set_bid_lotvalues(bid, self.initial_lots)
        if self.initial_criteria:
            self.initial_criteria = deepcopy(self.initial_criteria)
            self.initial_criteria = set_tender_criteria(
                self.initial_criteria,
                self.initial_data.get("lots", []),
                self.initial_data.get("items", []),
            )


    def create_tender(self):
        data = deepcopy(self.initial_data)
        config = deepcopy(self.initial_config)
        response = self.app.post_json("/tenders", {"data": data, "config": config})
        tender = response.json["data"]
        self.tender_token = response.json["access"]["token"]
        self.tender_id = tender["id"]
        criteria = []
        if self.initial_criteria:
            response = self.app.post_json(
                "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
                {"data": self.initial_criteria}
            )
            criteria = response.json["data"]
        if self.guarantee_criterion:
            self.app.post_json(
                "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
                {
                    "data": getattr(self, "guarantee_criterion_data", contract_guarantee_criteria)
                },
                status=201
            )

        status = tender["status"]
        if self.initial_bids:
            self.initial_bids_tokens = {}
            response = self.set_status("active.tendering")
            # self.app.patch_json(f"/tenders/{self.tender_id}?acc_token={self.tender_token}", {"data": {}})
            status = response.json["data"]["status"]
            bids = []
            rrs = set_bid_responses(criteria)
            for bid in self.initial_bids:
                bid = bid.copy()
                if self.initial_criteria:
                    bid["requirementResponses"] = rrs
                bid, bid_token = self.create_bid(self.tender_id, bid)
                bid_id = bid["id"]
                bids.append(bid)
                self.initial_bids_tokens[bid_id] = bid_token
            self.initial_bids = bids
        if self.initial_status and self.initial_status != status:
            self.set_status(self.initial_status)


class TenderContentWebTest(BaseTenderWebTest):
    initial_data = test_tender_data
    initial_status = "active.enquiries"
    initial_bids = None
    initial_lots = None

    def setUp(self):
        super(TenderContentWebTest, self).setUp()
        self.create_tender()
