import json
import os
from base64 import b64encode
from datetime import datetime, timedelta
from urllib.parse import urlencode
from uuid import uuid4

from nacl.encoding import HexEncoder
from requests.models import Response
from webtest import AppError

from openprocurement.api.constants import SESSION, TWO_PHASE_COMMIT_FROM, TZ
from openprocurement.api.procedure.utils import apply_data_patch
from openprocurement.api.tests.base import BaseWebTest as BaseApiWebTest
from openprocurement.api.utils import get_now
from openprocurement.tender.core.procedure.models.qualification_milestone import (
    QualificationMilestoneCodes,
)
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.tender.core.utils import calculate_tender_date
from openprocurement.tender.open.constants import ABOVE_THRESHOLD, COMPETITIVE_ORDERING

now = datetime.now()

current_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(current_dir, "data", "exclusion_criteria.json")) as json_file:
    test_exclusion_criteria = json.load(json_file)

test_requirement_groups = test_exclusion_criteria[0]["requirementGroups"]

with open(os.path.join(current_dir, "data", "lang_criteria.json")) as json_file:
    test_language_criteria = json.load(json_file)

with open(os.path.join(current_dir, "data", "tender_guarantee_criteria.json")) as json_file:
    test_tender_guarantee_criteria = json.load(json_file)

with open(os.path.join(current_dir, "data", "contract_guarantee_criteria.json")) as json_file:
    test_contract_guarantee_criteria = json.load(json_file)

with open(os.path.join(current_dir, "data", "lcc_lot_criteria.json")) as json_file:
    test_lcc_lot_criteria = json.load(json_file)

with open(os.path.join(current_dir, "data", "lcc_tender_criteria.json")) as json_file:
    test_lcc_tender_criteria = json.load(json_file)

with open(os.path.join(current_dir, "data", "technical_feature_criteria.json")) as json_file:
    test_tech_feature_criteria = json.load(json_file)


def get_criteria_by_ids(criteria, ids):
    return [c for c in criteria if c["classification"]["id"] in ids]


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
    initial_status = None
    initial_bids = None
    initial_lots = None

    tender_id = None

    periods = None
    now = None
    tender_class = None

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
            self.add_notice_doc(tender["data"]["id"], tender["access"]["token"])
        response = self.app.patch_json(
            f"/tenders/{tender['data']['id']}?acc_token={tender['access']['token']}",
            {"data": {"status": status}},
        )

        assert response.status == "200 OK"
        return response

    def create_bid(self, tender_id, bid_data, status=None):
        response = self.app.post_json("/tenders/{}/bids".format(tender_id), {"data": bid_data})
        token = response.json["access"]["token"]

        bid = response.json["data"]
        if bid_data.get("status", "") != "draft" and get_now() > TWO_PHASE_COMMIT_FROM:
            response = self.set_responses(tender_id, response.json, status=status)
            if response.json and "data" in response.json:
                bid = response.json["data"]

        return bid, token

    def set_responses(self, tender_id, bid, status=None):
        # pylint: disable-next=import-outside-toplevel, cyclic-import
        from openprocurement.tender.core.tests.criteria_utils import generate_responses

        tender = self.mongodb.tenders.get(tender_id)

        if not status:
            status = "pending"

        patch_data = {"status": status}
        if "requirementResponses" not in bid["data"]:
            rr = generate_responses(self, tender_id)
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
                    if "lotValues" in bid:
                        for lot_value in bid["lotValues"]:
                            if lot_value["status"] == "pending":
                                lot_value.update({"status": "active"})
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
        elif status == "active.qualification":
            self.activate_bids()
        elif status == "active.awarded":
            self.activate_bids()

        if extra:
            self.tender_document_patch.update(extra)

        self.save_changes()
        return self.get_tender()

    def add_notice_doc(self, tender_id, tender_token):
        response = self.app.post_json(
            f"/tenders/{tender_id}/documents?acc_token={tender_token}",
            {
                "data": {
                    "title": "sign.p7s",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/pdf",
                    "documentType": "notice",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")

    def add_qualification_sign_doc(self, tender_id, tender_token):
        response = self.app.post_json(
            f"/tenders/{tender_id}/documents?acc_token={tender_token}",
            {
                "data": {
                    "title": "sign.p7s",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/pdf",
                    "documentType": "evaluationReports",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")

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
                    "code": QualificationMilestoneCodes.CODE_24_HOURS.value,
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
