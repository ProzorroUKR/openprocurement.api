# -*- coding: utf-8 -*-
import os
from contextlib import contextmanager

from uuid import uuid4
from urllib import urlencode
from base64 import b64encode
from datetime import datetime, timedelta
from requests.models import Response

from openprocurement.tender.core.models import QualificationMilestone
from openprocurement.api.tests.base import BaseWebTest as BaseApiWebTest
from openprocurement.api.utils import SESSION, apply_data_patch, get_now
from openprocurement.tender.core.utils import (
    calculate_tender_date,
    calculate_tender_business_date,
)

now = datetime.now()


def bad_rs_request(method, url, **kwargs):
    response = Response()
    response.status_code = 403
    response.encoding = "application/json"
    response._content = '"Unauthorized: upload_view failed permission check"'
    response.reason = "403 Forbidden"
    return response


srequest = SESSION.request


class BaseWebTest(BaseApiWebTest):
    initial_auth = ("Basic", ("token", ""))
    docservice = False
    docservice_url = "http://localhost"
    relative_to = os.path.dirname(__file__)

    def setUp(self):
        super(BaseWebTest, self).setUp()
        if self.docservice:
            self.setUpDS()

    def setUpDS(self):
        self.app.app.registry.docservice_url = self.docservice_url
        test = self

        def request(method, url, **kwargs):
            response = Response()
            if method == "POST" and "/upload" in url:
                url = test.generate_docservice_url()
                response.status_code = 200
                response.encoding = "application/json"
                data = '{{"url":"{url}","hash":"md5:{md5}","format":"{format}","title":"{title}"}}'.format(
                    url=url, md5="0" * 32, title="name.doc", format="application/msword"
                )
                response._content = '{{"data": {data},"get_url":"{url}"}}'.format(url=url, data=data)
                response.reason = "200 OK"
            return response

        SESSION.request = request

    def generate_docservice_url(self):
        uuid = uuid4().hex
        key = self.app.app.registry.docservice_key
        keyid = key.hex_vk()[:8]
        signature = b64encode(key.signature("{}\0{}".format(uuid, "0" * 32)))
        query = {"Signature": signature, "KeyID": keyid}
        return "{}/get/{}?{}".format(self.docservice_url, uuid, urlencode(query))

    def tearDownDS(self):
        SESSION.request = srequest
        self.app.app.registry.docservice_url = None

    def tearDown(self):
        if self.docservice:
            self.tearDownDS()
        super(BaseWebTest, self).tearDown()


class BaseCoreWebTest(BaseWebTest):
    initial_data = None
    initial_status = None
    initial_bids = None
    initial_lots = None
    docservice = False

    tender_id = None

    periods = None
    now = None
    tender_class = None

    def tearDown(self):
        self.delete_tender()
        super(BaseCoreWebTest, self).tearDown()

    def set_status(self, status, extra=None, startend="start"):
        self.now = get_now()
        self.tender_document = self.db.get(self.tender_id)
        self.tender_document_patch = {"status": status}
        self.update_periods(status, startend=startend)
        if extra:
            self.tender_document_patch.update(extra)
        self.save_changes()
        return self.get_tender("chronograph")

    def update_periods(self, status, startend="start", shift=None):
        shift = shift or timedelta()
        if status in self.periods:
            for period in self.periods[status][startend]:
                self.tender_document_patch.update({period: {}})
                for date in self.periods[status][startend][period]:
                    self.tender_document_patch[period][date] = (self.calculate_period_date(
                        date, period, startend, status
                    ) + shift).isoformat()

            lots = self.tender_document.get("lots", [])
            if lots:
                for period in self.periods[status][startend]:
                    if period in ("auctionPeriod",):
                        for lot in lots:
                            if lot.get("status", None) == "active":
                                lot.update({period: {}})
                                for date in self.periods[status][startend][period]:
                                    lot[period][date] = (self.calculate_period_date(
                                        date, period, startend, status
                                    ) + shift).isoformat()
                self.tender_document_patch.update({"lots": lots})

    def calculate_period_date(self, date, period, startend, status):
        tender = self.tender_class(self.tender_document)
        period_date_item = self.periods[status][startend][period][date]
        return calculate_tender_date(
            self.now, period_date_item, tender=tender, working_days=False
        )

    def time_shift(self, status, extra=None, startend="start", shift=None):
        self.now = get_now()
        self.tender_document = self.db.get(self.tender_id)
        self.tender_document_patch = {}
        self.update_periods(status, startend=startend, shift=shift)
        if extra:
            self.tender_document_patch.update(extra)
        self.save_changes()

    def save_changes(self):
        if self.tender_document_patch:
            patch = apply_data_patch(self.tender_document, self.tender_document_patch)
            self.tender_document.update(patch)
            self.db.save(self.tender_document)
            self.tender_document = self.db.get(self.tender_id)
            self.tender_document_patch = {}

    def get_tender(self, role):
        with change_auth(self.app, ("Basic", (role, ""))):
            url = "/tenders/{}".format(self.tender_id)
            response = self.app.get(url)
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
        return response

    def check_chronograph(self, data=None):
        with change_auth(self.app, ("Basic", ("chronograph", ""))):
            url = "/tenders/{}".format(self.tender_id)
            data = data or {"data": {"id": self.tender_id}}
            response = self.app.patch_json(url, data)
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
        return response

    def delete_tender(self):
        if self.tender_id:
            self.db.delete(self.db[self.tender_id])

    def append_24hours_milestone(self, bid_id):
        tender = self.db.get(self.tender_id)
        now = get_now()
        qualification = {
            "id": "0" * 32,
            "bidID": bid_id,
            "status": "pending",
            "milestones": [
                {
                    "id": "0" * 32,
                    "code": QualificationMilestone.CODE_24_HOURS,
                    "date": now.isoformat(),
                    "dueDate": (now + timedelta(hours=24)).isoformat(),
                }
            ]
        }
        if tender["procurementMethodType"] in ("aboveThresholdUA", "aboveThresholdUA.defense",
                                               "competitiveDialogueUA.stage2"):
            qualification["bid_id"] = bid_id
            del qualification["bidID"]
            tender["awards"] = [qualification]
        else:
            tender["qualifications"] = [qualification]
        self.db.save(tender)

    def add_contract_proforma_document(self):
        data = {
            "id": uuid4().hex,
            "author": "tender_owner",
            "title": u"paper0000001.pdf",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/pdf",
            "templateId": "paper00000001",
            "documentType": "contractProforma",
            "documentOf": "tender",
            "dateModified": now.isoformat(),
            "datePublished": now.isoformat(),
        }
        if self.initial_lots:
            data["relatedItem"] = self.initial_lots[0]["id"]
            data["documentOf"] = "lot"
        doc = self.db.get(self.tender_id)
        proforma_docs = [d["id"] for d in doc.get("documents", []) if d.get("documentType", "") == "contractProforma"]
        if len(proforma_docs) != 0:
            self.proforma_doc_id = proforma_docs[-1]
        else:
            documents = doc.get("documents", [])
            documents.append(data)
            doc["documents"] = documents
            self.db.save(doc)
            self.proforma_doc_id = data["id"]


@contextmanager
def change_auth(app, auth):
    authorization = app.authorization
    app.authorization = auth
    yield app
    app.authorization = authorization
