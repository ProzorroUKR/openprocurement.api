# -*- coding: utf-8 -*-
import os
from hashlib import sha512
from datetime import datetime, timedelta
from uuid import uuid4
from copy import deepcopy
from mock import patch
from openprocurement.api.constants import SANDBOX_MODE
from openprocurement.api.utils import get_now
from openprocurement.api.tests.base import BaseWebTest
from openprocurement.tender.competitivedialogue.models import (
    TenderStage2UA, CompetitiveDialogEU, CompetitiveDialogUA,
    TenderStage2EU,
)
from openprocurement.tender.competitivedialogue.tests.periods import PERIODS, PERIODS_UA_STAGE_2
from openprocurement.tender.openua.tests.base import BaseTenderUAWebTest as BaseTenderWebTest
from openprocurement.tender.belowthreshold.tests.base import test_organization
from openprocurement.tender.openeu.tests.base import (
    test_tender_data as base_test_tender_data_eu,
    test_features_tender_data,
    test_bids,
)
from openprocurement.tender.competitivedialogue.constants import (
    CD_EU_TYPE,
    CD_UA_TYPE,
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.openua.tests.base import test_tender_data as base_test_tender_data_ua

test_bids = deepcopy(test_bids)
test_bids.append(deepcopy(test_bids[0]))  # Minimal number of bits is 3

now = datetime.now()
test_tender_data_eu = deepcopy(base_test_tender_data_eu)
test_tender_data_eu["procurementMethodType"] = CD_EU_TYPE
test_tender_data_ua = deepcopy(base_test_tender_data_eu)
del test_tender_data_ua["title_en"]
test_tender_data_ua["procurementMethodType"] = CD_UA_TYPE
test_tender_data_ua["tenderPeriod"]["endDate"] = (now + timedelta(days=31)).isoformat()


# stage 2
test_tender_stage2_data_eu = deepcopy(base_test_tender_data_eu)
test_tender_stage2_data_ua = deepcopy(base_test_tender_data_ua)
test_tender_stage2_data_eu["procurementMethodType"] = STAGE_2_EU_TYPE
test_tender_stage2_data_ua["procurementMethodType"] = STAGE_2_UA_TYPE
test_tender_stage2_data_eu["procurementMethod"] = "selective"
test_tender_stage2_data_ua["procurementMethod"] = "selective"
test_shortlistedFirms = [
    {
        "identifier": {
            "scheme": test_organization["identifier"]["scheme"],
            "id": u"00037257",
            "uri": test_organization["identifier"]["uri"],
        },
        "name": "Test org name 1",
    },
    {
        "identifier": {
            "scheme": test_organization["identifier"]["scheme"],
            "id": u"00037257",
            "uri": test_organization["identifier"]["uri"],
        },
        "name": "Test org name 2",
    },
    {
        "identifier": {
            "scheme": test_organization["identifier"]["scheme"],
            "id": u"00037257",
            "uri": test_organization["identifier"]["uri"],
        },
        "name": "Test org name 3",
    },
]
test_access_token_stage1 = uuid4().hex
test_tender_stage2_data_eu["shortlistedFirms"] = test_shortlistedFirms
test_tender_stage2_data_ua["shortlistedFirms"] = test_shortlistedFirms
test_tender_stage2_data_eu["dialogue_token"] = sha512(test_access_token_stage1).hexdigest()
test_tender_stage2_data_ua["dialogue_token"] = sha512(test_access_token_stage1).hexdigest()
test_tender_stage2_data_ua["owner"] = "broker"
test_tender_stage2_data_eu["owner"] = "broker"
test_tender_stage2_data_ua["status"] = "draft"
test_tender_stage2_data_eu["status"] = "draft"
test_tender_stage2_data_ua["tenderPeriod"]["endDate"] = (now + timedelta(days=31)).isoformat()
test_tender_stage2_data_eu["tenderPeriod"]["endDate"] = (now + timedelta(days=31)).isoformat()
test_tender_stage2_data_ua["dialogueID"] = uuid4().hex
test_tender_stage2_data_eu["dialogueID"] = uuid4().hex
test_tender_stage2_data_ua["items"][0]["classification"]["scheme"] = "CPV"
test_tender_stage2_data_eu["items"][0]["classification"]["scheme"] = "CPV"

test_lots = [
    {
        "title": "lot title",
        "description": "lot description",
        "value": test_tender_data_eu["value"],
        "minimalStep": test_tender_data_eu["minimalStep"],
    }
]

test_features_tender_eu_data = deepcopy(test_features_tender_data)
test_features_tender_eu_data["procurementMethodType"] = CD_EU_TYPE

test_tenderer = deepcopy(test_bids[0]["tenderers"][0])
test_tenderer["identifier"]["id"] = test_shortlistedFirms[0]["identifier"]["id"]
test_tenderer["identifier"]["scheme"] = test_shortlistedFirms[0]["identifier"]["scheme"]

test_author = deepcopy(test_tenderer)
del test_author["scale"]


if SANDBOX_MODE:
    test_tender_data_eu["procurementMethodDetails"] = "quick, accelerator=1440"
    test_tender_data_ua["procurementMethodDetails"] = "quick, accelerator=1440"


class BaseCompetitiveDialogApiWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)


class BaseCompetitiveDialogWebTest(BaseTenderWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = None
    initial_status = None
    initial_bids = None
    initial_lots = None
    initial_auth = None
    forbidden_lot_actions_status = (
        "unsuccessful"
    )  # status, in which operations with tender lots (adding, updating, deleting) are forbidden

    def set_enquiry_period_end(self):
        self.set_status("active.tendering", startend="enquiry_end")

    def set_complaint_period_end(self):
        self.set_status("active.tendering", startend="complaint_end")

    def setUp(self):
        super(BaseCompetitiveDialogWebTest, self).setUp()
        self.app.authorization = self.initial_auth or ("Basic", ("broker", ""))


class BaseCompetitiveDialogEUStage2WebTest(BaseCompetitiveDialogWebTest):
    initial_data = test_tender_stage2_data_eu
    test_bids_data = test_bids

    periods = PERIODS
    tender_class = TenderStage2EU


class BaseCompetitiveDialogUAStage2WebTest(BaseCompetitiveDialogWebTest):
    initial_data = test_tender_stage2_data_ua
    test_bids_data = test_bids

    periods = PERIODS_UA_STAGE_2
    tender_class = TenderStage2UA


class BaseCompetitiveDialogEUWebTest(BaseCompetitiveDialogWebTest):
    initial_data = test_tender_data_eu
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
    tender_class = CompetitiveDialogEU


class BaseCompetitiveDialogUAWebTest(BaseCompetitiveDialogWebTest):
    initial_data = test_tender_data_ua
    # auction role actions
    forbidden_auction_actions_status = (
        "active.tendering"
    )  # status, in which operations with tender auction (getting auction info, reporting auction results, updating auction urls) and adding tender documents are forbidden
    forbidden_auction_document_create_actions_status = (
        "active.tendering"
    )  # status, in which adding document to tender auction is forbidden

    periods = PERIODS
    tender_class = CompetitiveDialogUA


class BaseCompetitiveDialogUAContentWebTest(BaseCompetitiveDialogUAWebTest):
    initial_data = test_tender_data_ua
    initial_status = None
    initial_bids = None
    initial_lots = None

    def setUp(self):
        self.app.authorization = ("Basic", ("broker", ""))
        super(BaseCompetitiveDialogUAContentWebTest, self).setUp()
        self.create_tender()

    periods = PERIODS
    tender_class = CompetitiveDialogUA


class BaseCompetitiveDialogEUContentWebTest(BaseCompetitiveDialogEUWebTest):
    initial_data = test_tender_data_eu
    initial_status = None
    initial_bids = None
    initial_lots = None

    def setUp(self):
        self.app.authorization = ("Basic", ("broker", ""))
        super(BaseCompetitiveDialogEUContentWebTest, self).setUp()
        self.create_tender()


class BaseCompetitiveDialogEUStage2ContentWebTest(BaseCompetitiveDialogEUWebTest):
    initial_data = test_tender_stage2_data_eu
    initial_status = None
    initial_bids = None
    initial_lots = None
    initial_features = None

    tender_class = TenderStage2EU
    periods = PERIODS

    def setUp(self):
        self.app.authorization = ("Basic", ("broker", ""))
        super(BaseCompetitiveDialogEUStage2ContentWebTest, self).setUp()
        self.create_tender()

    def create_tender(self, initial_lots=None, initial_data=None, features=None, initial_bids=None):
        return create_tender_stage2(
            self,
            initial_lots=initial_lots,
            initial_data=initial_data,
            features=features,
            initial_bids=initial_bids
        )


class BaseCompetitiveDialogUAStage2ContentWebTest(BaseCompetitiveDialogUAWebTest):
    initial_data = test_tender_stage2_data_ua
    initial_status = None
    initial_bids = None
    initial_lots = None
    initial_features = None

    tender_class = TenderStage2UA
    periods = PERIODS_UA_STAGE_2

    def create_tenderers(self, count=1):
        tenderers = []
        for i in xrange(count):
            tenderer = deepcopy(test_bids[0]["tenderers"])
            identifier = self.initial_data["shortlistedFirms"][i if i < 3 else 3]["identifier"]
            tenderer[0]["identifier"]["id"] = identifier["id"]
            tenderer[0]["identifier"]["scheme"] = identifier["scheme"]
            tenderers.append(tenderer)
        return tenderers

    def setUp(self):
        self.app.authorization = ("Basic", ("broker", ""))
        super(BaseCompetitiveDialogUAStage2ContentWebTest, self).setUp()
        self.create_tender()

    def create_tender(self, initial_lots=None, initial_data=None, features=None, initial_bids=None):
        return create_tender_stage2(
            self,
            initial_lots=initial_lots,
            initial_data=initial_data,
            features=features,
            initial_bids=initial_bids
        )


def create_tender_stage2(self, initial_lots=None, initial_data=None, features=None, initial_bids=None):
    if initial_lots is None:
        initial_lots = self.initial_lots
    if initial_data is None:
        initial_data = self.initial_data
    if initial_bids is None:
        initial_bids = self.initial_bids
    auth = self.app.authorization
    self.app.authorization = ("Basic", ("competitive_dialogue", ""))
    data = deepcopy(initial_data)
    if initial_lots:  # add lots
        lots = []
        for i in initial_lots:
            lot = deepcopy(i)
            if "id" not in lot:
                lot["id"] = uuid4().hex
            lots.append(lot)
        data["lots"] = self.lots = lots
        self.initial_lots = lots
        for i, item in enumerate(data["items"]):
            item["relatedLot"] = lots[i % len(lots)]["id"]
        for firm in data["shortlistedFirms"]:
            firm["lots"] = [dict(id=lot["id"]) for lot in lots]
        self.lots_id = [lot["id"] for lot in lots]
    if features:  # add features
        for feature in features:
            if feature["featureOf"] == "lot":
                feature["relatedItem"] = data["lots"][0]["id"]
            if feature["featureOf"] == "item":
                feature["relatedItem"] = data["items"][0]["id"]
        data["features"] = self.features = features
    response = self.app.post_json("/tenders", {"data": data})  # create tender
    tender = response.json["data"]
    self.assertEqual(tender["owner"], "broker")
    status = response.json["data"]["status"]
    self.tender = tender
    self.tender_token = response.json["access"]["token"]
    self.tender_id = tender["id"]
    self.app.authorization = ("Basic", ("competitive_dialogue", ""))
    self.app.patch_json(
        "/tenders/{id}?acc_token={token}".format(id=self.tender_id, token=self.tender_token),
        {"data": {"status": "draft.stage2"}},
    )

    if self.initial_criteria:
        self.app.post_json(
            "/tenders/{id}/criteria?acc_token={token}".format(id=self.tender_id, token=self.tender_token),
            {"data": self.initial_criteria},
        )
    self.app.authorization = ("Basic", ("broker", ""))
    with patch("openprocurement.tender.core.validation.RELEASE_ECRITERIA_ARTICLE_17", get_now() + timedelta(days=1)):
        self.app.patch_json(
            "/tenders/{id}?acc_token={token}".format(id=self.tender_id, token=self.tender_token),
            {"data": {"status": "active.tendering"}},
        )
    self.app.authorization = auth
    if initial_bids:
        self.initial_bids_tokens = {}
        response = self.set_status("active.tendering")
        status = response.json["data"]["status"]
        bids = []
        for i in initial_bids:
            if initial_lots:
                i = i.copy()
                value = i.pop("value")
                i["lotValues"] = [{"value": value, "relatedLot": l["id"]} for l in self.lots]
            response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": i})
            self.assertEqual(response.status, "201 Created")
            bids.append(response.json["data"])
            self.initial_bids_tokens[response.json["data"]["id"]] = response.json["access"]["token"]
        self.bids = self.initial_bids = bids

    if self.initial_status and self.initial_status != status:
        self.set_status(self.initial_status)
