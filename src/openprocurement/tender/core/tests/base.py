import json
import os
from base64 import b64encode
from copy import deepcopy
from datetime import datetime, timedelta
from urllib.parse import urlencode
from uuid import uuid4

import standards
from nacl.encoding import HexEncoder
from requests.models import Response
from webtest import AppError

from openprocurement.api.constants import SESSION, TZ
from openprocurement.api.constants_env import TWO_PHASE_COMMIT_FROM
from openprocurement.api.context import set_now
from openprocurement.api.procedure.utils import apply_data_patch
from openprocurement.api.tests.base import BaseWebTest as BaseApiWebTest
from openprocurement.api.utils import get_now
from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.core.procedure.models.qualification_milestone import (
    QualificationMilestoneCode,
)
from openprocurement.tender.core.tests.utils import (
    change_auth,
    set_bid_items,
    set_bid_lotvalues,
    set_bid_responses,
    set_tender_criteria,
    set_tender_lots,
)
from openprocurement.tender.core.utils import calculate_tender_date
from openprocurement.tender.open.constants import ABOVE_THRESHOLD

now = datetime.now()

current_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(current_dir, "data", "lcc_lot_criteria.json")) as json_file:
    test_lcc_lot_criteria = json.load(json_file)

with open(os.path.join(current_dir, "data", "lcc_tender_criteria.json")) as json_file:
    test_lcc_tender_criteria = json.load(json_file)


def get_criteria_by_ids(criteria, ids):
    return [c for c in criteria if c["classification"]["id"] in ids]


def get_criteria_by_ids_prefix(criteria, prefix):
    return [c for c in criteria if c["classification"]["id"].startswith(prefix)]


test_criteria_other = standards.load("criteria/other.json")
test_criteria_article_16 = standards.load("criteria/article_16.json")
test_criteria_article_17 = standards.load("criteria/article_17.json")

test_criteria_decree_1178 = standards.load("criteria/decree_1178.json")
test_criteria_lcc = standards.load("criteria/LCC.json")

test_criteria_all = []
test_criteria_all.extend(test_criteria_other)
test_criteria_all.extend(test_criteria_article_17)

test_other_criteria = get_criteria_by_ids_prefix(test_criteria_all, "CRITERION.OTHER")
test_exclusion_criteria = get_criteria_by_ids_prefix(test_criteria_all, "CRITERION.EXCLUSION")
test_selection_criteria = get_criteria_by_ids_prefix(test_criteria_all, "CRITERION.SELECTION")

test_language_criteria = get_criteria_by_ids(test_criteria_all, "CRITERION.OTHER.BID.LANGUAGE")
test_tender_guarantee_criteria = get_criteria_by_ids(test_criteria_all, "CRITERION.OTHER.BID.GUARANTEE")
test_contract_guarantee_criteria = get_criteria_by_ids(test_criteria_all, "CRITERION.OTHER.CONTRACT.GUARANTEE")
test_localization_criteria = get_criteria_by_ids(
    test_criteria_all, "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.LOCAL_ORIGIN_LEVEL"
)

test_tech_feature_criteria = get_criteria_by_ids_prefix(
    test_criteria_all, "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.TECHNICAL_FEATURES"
)

test_article_16_criteria = test_criteria_article_16
test_lcc_criteria = test_criteria_lcc

test_main_criteria = []
test_main_criteria.extend(
    [
        criterion
        for criterion in test_other_criteria
        if criterion not in test_tender_guarantee_criteria
        and criterion not in test_contract_guarantee_criteria
        and criterion not in test_tech_feature_criteria
        and criterion not in test_localization_criteria
    ]
)
test_main_criteria.extend(test_exclusion_criteria)
test_main_criteria.extend(test_selection_criteria)

test_default_criteria = []
test_default_criteria.extend(test_main_criteria)
test_default_criteria.extend(test_article_16_criteria[:1])


test_requirement_groups = test_exclusion_criteria[0]["requirementGroups"]


srequest = SESSION.request


class BaseWebTest(BaseApiWebTest):
    initial_auth = ("Basic", ("token", ""))
    docservice_url = "http://localhost"
    relative_to = os.path.dirname(__file__)

    def setUp(self):
        super().setUp()
        self.setUpDS()

    def setUpDS(self):
        self.app.app.registry.docservice_url = self.docservice_url

        def request(method, url, **kwargs):
            response = Response()
            if method == "POST" and "/upload" in url:
                url = self.generate_docservice_url()
                response.status_code = 200
                response.encoding = "application/json"
                data = '{{"url":"{url}","hash":"md5:{md5}","format":"{format}","title":"{title}"}}'.format(
                    url=url, md5="0" * 32, title="name.doc", format="application/msword"
                )
                response._content = '{{"data": {data},"get_url":"{url}"}}'.format(url=url, data=data).encode()
                response.reason = "200 OK"
            return response

        SESSION.request = request

    def generate_docservice_url(self, doc_hash=None):
        uuid = uuid4().hex
        doc_hash = doc_hash or '0' * 32
        registry = self.app.app.registry
        signer = registry.docservice_key
        keyid = signer.verify_key.encode(encoder=HexEncoder)[:8].decode()
        msg = "{}\0{}".format(uuid, doc_hash).encode()
        signature = b64encode(signer.sign(msg).signature)
        query = {"Signature": signature, "KeyID": keyid}
        return "{}/get/{}?{}".format(self.docservice_url, uuid, urlencode(query))

    def get_doc_id_from_url(self, url):
        ds_url_start = f"{self.docservice_url}/get/"
        if url.startswith(ds_url_start):
            prefix_len = len(ds_url_start)
            return url[prefix_len : prefix_len + 32]
        else:
            return url.split("?download=")[1]

    def tearDownDS(self):
        SESSION.request = srequest
        self.app.app.registry.docservice_url = None

    def tearDown(self):
        self.tearDownDS()
        super().tearDown()


class BaseCoreWebTest(BaseWebTest):
    initial_data = None
    initial_config = None
    initial_criteria = None
    initial_status = None
    initial_bids = None
    initial_lots = None
    initial_agreement_data = None

    tender_for_funders = None
    guarantee_criterion = None

    agreement_id = None
    tender_id = None

    periods = None
    now = None
    tender_class = None

    def setUp(self):
        super().setUp()
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

    def tearDown(self):
        self.delete_tender()
        super().tearDown()

    def set_initial_status(self, tender, status=None):
        if not status:
            status = self.primary_tender_status

        # pylint: disable-next=import-outside-toplevel, cyclic-import
        from openprocurement.tender.core.tests.criteria_utils import add_criteria

        add_criteria(self, tender["data"]["id"], tender["access"]["token"])
        if "active" in status:
            self.add_sign_doc(tender["data"]["id"], tender["access"]["token"])
        response = self.app.patch_json(
            f"/tenders/{tender['data']['id']}?acc_token={tender['access']['token']}",
            {"data": {"status": status}},
        )

        assert response.status == "200 OK"
        return response

    def create_bid(self, tender_id, bid_data, status=None):
        tender = self.mongodb.tenders.get(tender_id)
        if tender.get("lots") and not bid_data.get("lotValues"):
            set_bid_lotvalues(bid_data, tender["lots"])
        if not bid_data.get("items"):
            set_bid_items(self, bid_data, tender["items"], tender_id=tender_id)

        response = self.app.post_json("/tenders/{}/bids".format(tender_id), {"data": bid_data})
        token = response.json["access"]["token"]

        bid = response.json["data"]
        if bid_data.get("status", "") != "draft" and get_now() > TWO_PHASE_COMMIT_FROM:
            response = self.set_responses(tender_id, response.json, status=status)
            if response.json and "data" in response.json:
                bid = response.json["data"]

        return bid, token

    def add_sign_doc(self, tender_id, owner_token, docs_url="/documents", document_type="notice", doc_id=None):
        request_body = {
            "data": {
                "title": "sign.p7s",
                "documentType": document_type,
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "sign/pkcs7-signature",
            }
        }

        if doc_id:
            response = self.app.put_json(
                f"/tenders/{tender_id}{docs_url}/{doc_id}?acc_token={owner_token}",
                request_body,
            )
        else:
            response = self.app.post_json(
                f"/tenders/{tender_id}{docs_url}?acc_token={owner_token}",
                request_body,
            )
        return response

    def activate_bid(self, tender_id, bid_id, bid_token, doc_id=None):
        self.add_sign_doc(
            tender_id, bid_token, docs_url=f"/bids/{bid_id}/documents", document_type="proposal", doc_id=doc_id
        )
        response = self.app.patch_json(
            f"/tenders/{tender_id}/bids/{bid_id}?acc_token={bid_token}",
            {"data": {"status": "pending"}},
        )
        return response

    def set_responses(self, tender_id, bid, status=None):
        if not status:
            status = "pending"

        patch_data = {"status": status}
        if "requirementResponses" not in bid["data"]:
            response = self.app.get("/tenders/{}".format(tender_id))
            tender = response.json["data"]
            rr = set_bid_responses(tender.get("criteria", []))
            if rr:
                patch_data["requirementResponses"] = rr

        response = self.app.patch_json(
            f"/tenders/{tender_id}/bids/{bid['data']['id']}?acc_token={bid['access']['token']}",
            {"data": patch_data},
        )
        assert response.status == "200 OK"
        return response

    def activate_bids(self):
        if self.tender_document.get("bids", ""):
            bids = self.tender_document["bids"]
            for bid in bids:
                if bid["status"] == "pending":
                    bid.update({"status": "active"})
                    if "value" in bid:
                        bid["initialValue"] = bid["value"]
                    if "lotValues" in bid:
                        for lot_value in bid["lotValues"]:
                            if lot_value["status"] == "pending":
                                lot_value.update({"status": "active", "date": get_now().isoformat()})
                                lot_value["initialValue"] = lot_value["value"]
            self.tender_document_patch.update({"bids": bids})

    def set_status(self, status, extra=None, startend="start"):
        self.now = get_now()
        self.tender_document = self.mongodb.tenders.get(self.tender_id)
        old_status = self.tender_document["status"]
        self.tender_document_patch = {"status": status}
        self.update_periods(status, startend=startend)

        if status == "active.pre-qualification.stand-still":
            self.activate_bids()
        elif status == "active.auction":
            self.activate_bids()
            self.update_qualification_complaint_periods()
        elif status == "active.qualification":
            self.activate_bids()
            self.update_qualification_complaint_periods()
        elif status == "active.awarded":
            self.activate_bids()
            self.update_qualification_complaint_periods()
        elif status == "active.stage2.pending":
            self.update_qualification_complaint_periods()

        if extra:
            self.tender_document_patch.update(extra)

        self.save_changes()
        return self.get_tender()

    def update_qualification_complaint_periods(self):
        qualifications = self.tender_document.get("qualifications")
        if qualifications:
            complain_duration = self.tender_document["config"]["qualificationComplainDuration"]
            for qualification in qualifications:
                complaint_period = qualification.get("complaintPeriod")
                if complaint_period and complaint_period.get("endDate"):
                    start_date = get_now() - timedelta(days=complain_duration)
                    qualification["complaintPeriod"]["startDate"] = start_date.isoformat()
                    qualification["complaintPeriod"]["endDate"] = get_now().isoformat()
            self.tender_document_patch.update({"qualifications": qualifications})

    def update_periods(self, status, startend="start", shift=None):
        shift = shift or timedelta()
        if status in self.periods:
            for period in self.periods[status][startend]:
                self.tender_document_patch.update({period: {}})
                for date in self.periods[status][startend][period]:
                    self.tender_document_patch[period][date] = (
                        (self.calculate_period_date(date, period, startend, status) + shift).astimezone(TZ).isoformat()
                    )

            lots = self.tender_document.get("lots", [])
            if lots:
                for period in self.periods[status][startend]:
                    if period in ("auctionPeriod",):
                        for lot in lots:
                            if lot.get("status", None) == "active":
                                lot.update({period: {}})
                                for date in self.periods[status][startend][period]:
                                    lot[period][date] = (
                                        (self.calculate_period_date(date, period, startend, status) + shift)
                                        .astimezone(TZ)
                                        .isoformat()
                                    )
                self.tender_document_patch.update({"lots": lots})

    def calculate_period_date(self, date, period, startend, status):
        period_date_item = self.periods[status][startend][period][date]
        return calculate_tender_date(
            self.now,
            period_date_item,
            tender=self.tender_document,
            working_days=False,
        )

    def time_shift(self, status, extra=None, startend="start", shift=None):
        self.now = get_now()
        self.tender_document = self.mongodb.tenders.get(self.tender_id)
        self.tender_document_patch = {}
        self.update_periods(status, startend=startend, shift=shift)
        if extra:
            self.tender_document_patch.update(extra)
        if status != "active.pre-qualification.stand-still":
            self.update_qualification_complaint_periods()
        self.save_changes()

    def save_changes(self):
        if self.tender_document_patch:
            patch = apply_data_patch(self.tender_document, self.tender_document_patch)
            self.tender_document.update(patch)
            self.mongodb.tenders.save(self.tender_document)
            self.tender_document = self.mongodb.tenders.get(self.tender_id)
            self.tender_document_patch = {}

    def get_tender(self, role="token"):
        with change_auth(self.app, ("Basic", (role, ""))):
            url = "/tenders/{}".format(self.tender_id)
            response = self.app.get(url)
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
        return response

    def check_chronograph(self, data=None, status=200):
        with change_auth(self.app, ("Basic", ("chronograph", ""))):
            url = "/tenders/{}/chronograph".format(self.tender_id)
            data = data or {"data": {"id": self.tender_id}}
            try:
                response = self.app.patch_json(url, data, status=status)
            except AppError:
                # skip if there is no chronograph endpoint
                pass
            else:
                self.assertEqual(response.content_type, "application/json")
                self.tender_document = self.mongodb.tenders.get(self.tender_id)
                self.tender_document_patch = {}
                return response

    def delete_tender(self):
        if self.tender_id:
            self.mongodb.tenders.delete(self.tender_id)

    def append_24hours_milestone(self, bid_id):
        tender = self.mongodb.tenders.get(self.tender_id)
        now = get_now()
        qualification = {
            "id": "0" * 32,
            "bidID": bid_id,
            "status": "pending",
            "milestones": [
                {
                    "id": "0" * 32,
                    "code": QualificationMilestoneCode.CODE_24_HOURS.value,
                    "date": now.isoformat(),
                    "dueDate": (now + timedelta(hours=24)).isoformat(),
                }
            ],
        }
        if tender["procurementMethodType"] in (
            ABOVE_THRESHOLD,
            COMPETITIVE_ORDERING,
            "aboveThresholdUA",
            "aboveThresholdUA.defense",
            "simple.defense",
            "competitiveDialogueUA.stage2",
        ):
            qualification["bid_id"] = bid_id
            del qualification["bidID"]
            tender["awards"] = [qualification]
        else:
            tender["qualifications"] = [qualification]
        self.mongodb.tenders.save(tender)

    def create_tender(self, config=None):
        data = deepcopy(self.initial_data)
        config = config if config else deepcopy(self.initial_config)
        response = self.app.post_json("/tenders", {"data": data, "config": config})
        tender = response.json["data"]
        self.tender_token = response.json["access"]["token"]
        self.tender_id = tender["id"]
        criteria = []
        if self.initial_criteria:
            set_tender_criteria(
                self.initial_criteria,
                tender.get("lots", []),
                tender.get("items", []),
            )
            response = self.app.post_json(
                "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
                {"data": self.initial_criteria},
            )
            criteria = response.json["data"]
        if self.guarantee_criterion:
            guarantee_criteria = getattr(self, "guarantee_criterion_data", test_contract_guarantee_criteria)
            set_tender_criteria(
                guarantee_criteria,
                tender.get("lots", []),
                tender.get("items", []),
            )
            self.app.post_json(
                "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
                {"data": guarantee_criteria},
                status=201,
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
                set_bid_items(self, bid, tender["items"])
                if self.initial_criteria:
                    bid["requirementResponses"] = rrs
                if hasattr(self, "initial_bid_status") and self.initial_bid_status:
                    bid["status"] = self.initial_bid_status
                bid, bid_token = self.create_bid(self.tender_id, bid)
                bid_id = bid["id"]
                bids.append(bid)
                self.initial_bids_tokens[bid_id] = bid_token
            self.initial_bids = bids
        if self.initial_status and self.initial_status != status:
            self.set_status(self.initial_status)

    def create_agreement(self):
        if self.mongodb.agreements.get(self.agreement_id):
            self.delete_agreement()
        agreement = self.initial_agreement_data
        agreement["dateModified"] = get_now().isoformat()
        set_now()
        self.mongodb.agreements.save(agreement, insert=True)

    def delete_agreement(self):
        self.mongodb.agreements.delete(self.agreement_id)
