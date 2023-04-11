# -*- coding: utf-8 -*-
from datetime import timedelta, datetime
from isodate import duration_isoformat
from uuid import uuid4

from openprocurement.tender.cfaua.constants import CLARIFICATIONS_UNTIL_PERIOD, MAX_AGREEMENT_PERIOD
from openprocurement.tender.cfaua.tests.base import test_tender_cfaua_agreement_period
from openprocurement.tender.cfaua.models.submodels.agreement import Agreement


# TenderAgreementResourceTest


def get_tender_agreement(self):
    agreement_raw = self.app.app.registry.mongodb.tenders.get(self.tender_id)["agreements"][0]
    agreement = Agreement(agreement_raw).serialize("embedded")

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/agreements/{}".format(self.tender_id, agreement["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], agreement)
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.get("/tenders/{}/agreements/some_id".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "agreement_id"}]
    )

    response = self.app.get("/tenders/some_id/agreements/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )


def get_tender_agreements(self):
    agreement_keys = tuple(["id", "agreementID", "items", "status", "contracts", "date"])
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/agreements".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    for key in agreement_keys:
        self.assertIn(key, response.json["data"][0].keys())

    response = self.app.get("/tenders/some_id/agreements", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )


def patch_tender_agreement_datesigned(self):
    response = self.app.get("/tenders/{}/agreements".format(self.tender_id))
    agreement = response.json["data"][0]
    self.assertEqual(agreement["status"], "pending")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    self.assertEqual(tender["status"], "active.awarded")

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(self.tender_id, agreement["id"], self.tender_token),
        {"data": {"status": "active", "period": test_tender_cfaua_agreement_period}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't sign agreement without all contracts.unitPrices.value.amount",
                "location": "body",
                "name": "data",
            }
        ],
    )

    # Fill unitPrice.value.amount for all contracts in agreement
    response = self.app.get("/tenders/{}/agreements/{}/contracts".format(self.tender_id, self.agreement_id))
    contracts = response.json["data"]
    for contract in contracts:
        unit_prices = contract["unitPrices"]
        for unit_price in unit_prices:
            unit_price["value"]["amount"] = 60
        response = self.app.patch_json(
            "/tenders/{}/agreements/{}/contracts/{}?acc_token={}".format(
                self.tender_id, self.agreement_id, contract["id"], self.tender_token
            ),
            {"data": {"unitPrices": unit_prices}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(self.tender_id, self.agreement_id, self.tender_token),
        {"data": {"status": "active",
                  "dateSigned": tender["awardPeriod"]["endDate"],
                  "period": test_tender_cfaua_agreement_period}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "dateSigned",
                "description": [
                    "Agreement signature date should be after award complaint period end date ({})".format(
                        tender["awardPeriod"]["endDate"]
                    )
                ],
            }
        ],
    )

    # Set first contract.status in unsuccessful
    response = self.app.patch_json(
        "/tenders/{}/agreements/{}/contracts/{}?acc_token={}".format(
            self.tender_id, self.agreement_id, contracts[0]["id"], self.tender_token
        ),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(self.tender_id, self.agreement_id, self.tender_token),
        {"data": {"status": "active", "period": test_tender_cfaua_agreement_period}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [{"description": "Agreement don't reach minimum active contracts.", "location": "body", "name": "data"}],
    )

    # Set first contract.status in active
    response = self.app.patch_json(
        "/tenders/{}/agreements/{}/contracts/{}?acc_token={}".format(
            self.tender_id, self.agreement_id, contracts[0]["id"], self.tender_token
        ),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]

    # Agreement signing
    response = self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(self.tender_id, self.agreement_id, self.tender_token),
        {"data": {"status": "active", "period": test_tender_cfaua_agreement_period}},
        status=422,
    )
    end_date = tender["contractPeriod"]["clarificationsUntil"]
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Agreement signature date should be after contractPeriod.clarificationsUntil ({})".format(
                    end_date
                ),
            }
        ],
    )

    tender = self.mongodb.tenders.get(self.tender_id)
    tender["contractPeriod"]["startDate"] = (
        datetime.now() - CLARIFICATIONS_UNTIL_PERIOD - timedelta(days=1)
    ).isoformat()
    tender["contractPeriod"]["clarificationsUntil"] = (datetime.now() - timedelta(days=1)).isoformat()
    self.mongodb.tenders.save(tender)

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(self.tender_id, self.agreement_id, self.tender_token),
        {"data": {"status": "active", "period": {"startDate": datetime.now().isoformat()}}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["startDate and endDate are required in agreement.period."],
                "location": "body",
                "name": "period",
            }
        ],
    )

    now = datetime.now()
    start_date = now.isoformat()
    end_date = (now + timedelta(days=465 * 5)).isoformat()

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(self.tender_id, self.agreement_id, self.tender_token),
        {"data": {"status": "active", "period": {"startDate": start_date, "endDate": end_date}}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Agreement period can't be greater than {}.".format(
                    duration_isoformat(MAX_AGREEMENT_PERIOD)
                )],
                "location": "body",
                "name": "period",
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(self.tender_id, self.agreement_id, self.tender_token),
        {"data": {"status": "active", "period": test_tender_cfaua_agreement_period}},
    )
    contract = response.json["data"]["contracts"][0]

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertIn("dateSigned", response.json["data"].keys())

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(self.tender_id, agreement["id"], self.tender_token),
        {"data": {"status": "cancelled"}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't update agreement in current (complete) tender status",
                "location": "body",
                "name": "data",
            }
        ],
    )

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "complete")

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}/contracts/{}?acc_token={}".format(
            self.tender_id, agreement["id"], contract["id"], self.tender_token
        ),
        {"data": {"status": "unsuccessful"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can't update agreement in current (complete) tender status",
            }
        ],
    )


def agreement_termination(self):
    response = self.app.get("/tenders/{}/agreements".format(self.tender_id))
    agreement = response.json["data"][0]

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(self.tender_id, agreement["id"], self.tender_token),
        {"data": {"status": "terminated"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"],
        ["Value must be one of ['pending', 'active', 'cancelled', 'unsuccessful']."],
    )


def agreement_cancellation(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    self.assertEqual(tender["status"], "active.awarded")

    response = self.app.get("/tenders/{}/agreements".format(self.tender_id))
    agreement = response.json["data"][0]

    # Try sign agreement
    response = self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(self.tender_id, agreement["id"], self.tender_token),
        {"data": {"status": "active"}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [{"description": ["Period is required for agreement signing."], "location": "body", "name": "period"}],
    )

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(self.tender_id, agreement["id"], self.tender_token),
        {"data": {"status": "active", "period": test_tender_cfaua_agreement_period}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't sign agreement without all contracts.unitPrices.value.amount",
                "location": "body",
                "name": "data",
            }
        ],
    )

    # Agreement cancellation
    response = self.app.get("/tenders/{}/agreements/{}".format(self.tender_id, agreement["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")
    response = self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(self.tender_id, agreement["id"], self.tender_token),
        {"data": {"status": "cancelled"}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [{"description": "Can't update agreement status", "location": "body", "name": "data"}],
    )


def create_tender_agreement_document(self):
    response = self.app.post_json(
        "/tenders/{}/agreements/{}/documents?acc_token={}".format(self.tender_id, self.agreement_id, self.tender_token),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.assertEqual("name.doc", response.json["data"]["title"])
    key = self.get_doc_id_from_url(response.json["data"]["url"])

    response = self.app.get("/tenders/{}/agreements/{}/documents".format(self.tender_id, self.agreement_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get("/tenders/{}/agreements/{}/documents?all=true".format(self.tender_id, self.agreement_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get(
        "/tenders/{}/agreements/{}/documents/{}?download=some_id".format(self.tender_id, self.agreement_id, doc_id),
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "download"}]
    )

    response = self.app.get(
        "/tenders/{}/agreements/{}/documents/{}?download={}".format(self.tender_id, self.agreement_id, doc_id, key)
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)

    response = self.app.get("/tenders/{}/agreements/{}/documents/{}".format(self.tender_id, self.agreement_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    self.cancel_tender()

    response = self.app.post_json(
        "/tenders/{}/agreements/{}/documents?acc_token={}".format(self.tender_id, self.agreement_id, self.tender_token),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add document in current (cancelled) tender status"
    )


def put_tender_agreement_document(self):
    response = self.app.post_json(
        "/tenders/{}/agreements/{}/documents?acc_token={}".format(self.tender_id, self.agreement_id, self.tender_token),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.put_json(
        "/tenders/{}/agreements/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.agreement_id, doc_id, self.tender_token
        ),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = self.get_doc_id_from_url(response.json["data"]["url"])

    response = self.app.get(
        "/tenders/{}/agreements/{}/documents/{}?download={}".format(self.tender_id, self.agreement_id, doc_id, key)
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)

    response = self.app.get("/tenders/{}/agreements/{}/documents/{}".format(self.tender_id, self.agreement_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    response = self.app.put_json(
        "/tenders/{}/agreements/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.agreement_id, doc_id, self.tender_token
        ),
        {"data": {
            "title": "укр.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = self.get_doc_id_from_url(response.json["data"]["url"])

    response = self.app.get(
        "/tenders/{}/agreements/{}/documents/{}?download={}".format(self.tender_id, self.agreement_id, doc_id, key)
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)

    self.cancel_tender()

    response = self.app.put_json(
        "/tenders/{}/agreements/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.agreement_id, doc_id, self.tender_token
        ),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update document in current (cancelled) tender status"
    )


def patch_tender_agreement_document(self):
    response = self.app.post_json(
        "/tenders/{}/agreements/{}/documents?acc_token={}".format(self.tender_id, self.agreement_id, self.tender_token),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.agreement_id, doc_id, self.tender_token
        ),
        {"data": {"description": "document description"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get("/tenders/{}/agreements/{}/documents/{}".format(self.tender_id, self.agreement_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("document description", response.json["data"]["description"])

    self.cancel_tender()

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.agreement_id, doc_id, self.tender_token
        ),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update document in current (cancelled) tender status"
    )


def patch_tender_agreement(self):
    response = self.app.get("/tenders/{}/agreements".format(self.tender_id))
    agreement = response.json["data"][0]

    fake_agreementID = "myselfID"
    fake_items_data = [{"description": "New Description"}]

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(self.tender_id, agreement["id"], self.tender_token),
        {"data": {"agreementID": fake_agreementID, "items": fake_items_data}},
        status=422,
    )
    self.assertCountEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "items",
                "description": "Rogue field"
            },
            {
                "location": "body",
                "name": "agreementID",
                "description": "Rogue field"
            },
        ]
    )

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(self.tender_id, agreement["id"], self.tender_token),
        {"data": {"status": "active", "period": test_tender_cfaua_agreement_period}},
        status=422,
    )
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't sign agreement without all contracts.unitPrices.value.amount",
                "location": "body",
                "name": "data",
            }
        ],
    )

    # Fill unitPrice.value.amount for all contracts in agreement
    response = self.app.get("/tenders/{}/agreements/{}/contracts".format(self.tender_id, self.agreement_id))
    contracts = response.json["data"]
    for contract in contracts:
        unit_prices = contract["unitPrices"]
        for unit_price in unit_prices:
            unit_price["value"]["amount"] = 60
        response = self.app.patch_json(
            "/tenders/{}/agreements/{}/contracts/{}?acc_token={}".format(
                self.tender_id, self.agreement_id, contract["id"], self.tender_token
            ),
            {"data": {"unitPrices": unit_prices}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]

    # Sign agreement
    response = self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(self.tender_id, self.agreement_id, self.tender_token),
        {"data": {"status": "active", "period": test_tender_cfaua_agreement_period}},
        status=422,
    )
    end_date = tender["contractPeriod"]["clarificationsUntil"]
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Agreement signature date should be after contractPeriod.clarificationsUntil ({})".format(
                    end_date
                ),
            }
        ],
    )

    tender = self.mongodb.tenders.get(self.tender_id)
    tender["contractPeriod"]["startDate"] = (
        datetime.now() - CLARIFICATIONS_UNTIL_PERIOD - timedelta(days=1)
    ).isoformat()
    tender["contractPeriod"]["clarificationsUntil"] = (datetime.now() - timedelta(days=1)).isoformat()
    self.mongodb.tenders.save(tender)

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(self.tender_id, self.agreement_id, self.tender_token),
        {"data": {"status": "active", "period": test_tender_cfaua_agreement_period}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertIn("dateSigned", response.json["data"].keys())
    response = self.get_tender("")
    # Tender complete
    self.assertEqual(response.json["data"]["status"], "complete")

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(self.tender_id, agreement["id"], self.tender_token),
        {"data": {"title": "New Title"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update agreement in current (complete) tender status"
    )

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(self.tender_id, agreement["id"], self.tender_token),
        {"data": {"status": "pending"}},
        status=403,
    )
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update agreement in current (complete) tender status"
    )

    response = self.app.patch_json(
        "/tenders/{}/agreements/some_id".format(self.tender_id), {"data": {"status": "active"}}, status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "agreement_id"}]
    )

    response = self.app.patch_json("/tenders/some_id/agreements/some_id", {"data": {"status": "active"}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    response = self.app.get("/tenders/{}/agreements/{}".format(self.tender_id, agreement["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(self.tender_id, self.agreement_id, self.tender_token),
        {"data": {"status": "cancelled"}},
        status=403,
    )
    self.assertEqual((response.status, response.content_type), ("403 Forbidden", "application/json"))
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't update agreement in current (complete) tender status",
                "location": "body",
                "name": "data",
            }
        ],
    )


def patch_tender_agreement_unsuccessful(self):

    self.set_status("active.awarded")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["status"], "active.awarded")

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(self.tender_id, self.agreement_id, self.tender_token),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["status"], "unsuccessful")

    response = self.app.get("/tenders/{}/agreements/{}".format(self.tender_id, self.agreement_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(self.tender_id, self.agreement_id, self.tender_token),
        {"data": {"status": "cancelled"}},
        status=403,
    )
    self.assertEqual((response.status, response.content_type), ("403 Forbidden", "application/json"))
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't update agreement in current (unsuccessful) tender status",
                "location": "body",
                "name": "data",
            }
        ],
    )

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def not_found(self):
    response = self.app.post_json(
        "/tenders/some_id/agreements/some_id/documents?acc_token={}".format(self.tender_token),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    response = self.app.post_json(
        "/tenders/{}/agreements/some_id/documents?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "agreement_id"}]
    )

    response = self.app.get("/tenders/some_id/agreements/some_id/documents", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    response = self.app.get("/tenders/{}/agreements/some_id/documents".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "agreement_id"}]
    )

    response = self.app.get("/tenders/some_id/agreements/some_id/documents/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    response = self.app.get("/tenders/{}/agreements/some_id/documents/some_id".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "agreement_id"}]
    )

    response = self.app.get(
        "/tenders/{}/agreements/{}/documents/some_id".format(self.tender_id, self.agreement_id), status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "document_id"}]
    )


# Agreement contracts
def get_tender_agreement_contracts(self):
    min_contracts_count = 3
    response = self.app.get("/tenders/{}/agreements".format(self.tender_id))
    agreement = response.json["data"][0]
    items_id = [i["id"] for i in agreement["items"]]

    self.assertEqual(agreement["status"], "pending")
    self.assertEqual(len(agreement["contracts"]), min_contracts_count)

    response = self.app.get("/tenders/{}/agreements/{}/contracts".format(self.tender_id, agreement["id"]))
    self.assertEqual(len(response.json["data"]), min_contracts_count)
    for contract in response.json["data"]:
        self.assertEqual(contract["status"], "active")
        for unit_price in contract["unitPrices"]:
            self.assertNotIn("amount", unit_price["value"])
            self.assertIn(unit_price["relatedItem"], items_id)

    response = self.app.get("/tenders/{}/agreements/some_agreement_id/contracts".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "agreement_id"}]
    )


def get_tender_agreement_contract(self):
    min_contracts_count = 3
    response = self.app.get("/tenders/{}".format(self.tender_id))
    agreement = response.json["data"]["agreements"][0]
    contracts = agreement["contracts"]
    items_id = [i["id"] for i in agreement["items"]]

    self.assertEqual(agreement["status"], "pending")
    self.assertEqual(len(agreement["contracts"]), min_contracts_count)

    for contract in contracts:
        response = self.app.get(
            "/tenders/{}/agreements/{}/contracts/{}".format(self.tender_id, agreement["id"], contract["id"])
        )
        self.assertEqual(contract, response.json["data"])
        self.assertEqual(contract["status"], "active")
        for unit_price in contract["unitPrices"]:
            self.assertNotIn("amount", unit_price["value"])
            self.assertIn(unit_price["relatedItem"], items_id)

    response = self.app.get(
        "/tenders/{}/agreements/{}/contracts/invalid_id".format(self.tender_id, agreement["id"]), status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "contract_id"}]
    )


def patch_tender_agreement_contract(self):
    response = self.app.get(
        "/tenders/{}/agreements/{}/contracts/{}".format(self.tender_id, self.agreement_id, self.contract_id)
    )
    contract = response.json["data"]
    self.assertEqual(contract["status"], "active")
    for unit_price in contract["unitPrices"]:
        self.assertNotIn("amount", unit_price["value"])

    related_item = contract["unitPrices"][0]["relatedItem"]
    response = self.app.patch_json(
        "/tenders/{}/agreements/{}/contracts/{}?acc_token={}".format(
            self.tender_id, self.agreement_id, self.contract_id, self.tender_token
        ),
        {
            "data": {
                "unitPrices": [{
                    "relatedItem": related_item,
                    "value": {"amount": 100, "currency": "UAH", "valueAddedTaxIncluded": True},
                }, {
                    "relatedItem": uuid4().hex,
                    "value": {"amount": 1, "currency": "UAH", "valueAddedTaxIncluded": True},
                }]
            }
        },
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "unitPrice.value.amount count doesn't match with contract.",
                "location": "body",
                "name": "data",
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}/contracts/{}?acc_token={}".format(
            self.tender_id, self.agreement_id, self.contract_id, self.tender_token
        ),
        {"data": {"unitPrices": [{
            "relatedItem": uuid4().hex,
            "value": {"amount": 1, "currency": "UAH", "valueAddedTaxIncluded": True},
        }]}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"], [{
            "description": "All relatedItem values doesn't match with contract.",
            "location": "body",
            "name": "data",
        }],
    )

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}/contracts/{}?acc_token={}".format(
            self.tender_id, self.agreement_id, self.contract_id, self.tender_token
        ),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}/contracts/{}?acc_token={}".format(
            self.tender_id, self.agreement_id, self.contract_id, self.tender_token
        ),
        {"data": {"unitPrices": [{
            "value": {"amount": 60, "currency": "RUB", "valueAddedTaxIncluded": False},
            "relatedItem": related_item,
        }]}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "currency of bid should be identical to currency of value of lot",
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}/contracts/{}?acc_token={}".format(
            self.tender_id, self.agreement_id, self.contract_id, self.tender_token
        ),
        {"data": {"unitPrices": [{
            "value": {"amount": 60, "currency": "UAH", "valueAddedTaxIncluded": False},
            "relatedItem": related_item,
        }]}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of lot",
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}/contracts/{}?acc_token={}".format(
            self.tender_id, self.agreement_id, self.contract_id, self.tender_token
        ),
        {"data": {"unitPrices": [{
            "value": {"amount": 60, "currency": "UAH", "valueAddedTaxIncluded": True},
            "relatedItem": related_item,
        }]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    self.assertEqual(response.json["data"]["unitPrices"][0]["value"]["amount"], 60)

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}/contracts/{}?acc_token={}".format(
            self.tender_id, self.agreement_id, self.contract_id, self.tender_token
        ),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertEqual(response.json["data"]["unitPrices"][0]["value"]["amount"], 60)

    # same
    response = self.app.patch_json(
        "/tenders/{}/agreements/{}/contracts/{}?acc_token={}".format(
            self.tender_id, self.agreement_id, self.contract_id, self.tender_token
        ),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")


def patch_lots_agreement_contract_unit_prices(self):
    self.tender_document_patch["agreements"] = self.tender_document["agreements"]
    self.tender_document_patch["agreements"][0]["items"][0]["quantity"] = 320000.0
    self.tender_document_patch["bids"] = self.tender_document["bids"]
    for bid in self.tender_document_patch["bids"]:
        bid["lotValues"][0]["value"]["amount"] = 25590000.0
    self.save_changes()

    response = self.app.get("/tenders/{}".format(self.tender_id))
    bid_id = response.json["data"]["bids"][-1]["id"]
    bid_value = response.json["data"]["bids"][-1]["lotValues"][0]["value"]["amount"]

    self.set_status("active.awarded")
    response = self.app.get("/tenders/{}/agreements".format(self.tender_id))
    agreement = response.json["data"][0]
    contract = [c for c in agreement["contracts"] if c["bidID"] == bid_id][0]
    related_item = contract["unitPrices"][0]["relatedItem"]

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}/contracts/{}?acc_token={}".format(
            self.tender_id, self.agreement_id, self.contract_id, self.tender_token
        ),
        {"data": {"unitPrices": [{
            "value": {"amount": 79.968, "currency": "UAH", "valueAddedTaxIncluded": True},
            "relatedItem": related_item,
        }]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertEqual(response.json["data"]["unitPrices"][0]["value"]["amount"], 79.968)

    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    bids = response.json["data"]
    bid_id = [b for b in bids if b["lotValues"][0]["value"]["amount"] == bid_value][0]["id"]
    contract = [c for c in agreement["contracts"] if c["bidID"] == bid_id][0]

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}/contracts/{}?acc_token={}".format(
            self.tender_id, agreement["id"], contract["id"], self.tender_token
        ),
        {"data": {"unitPrices": [
            {"value": {"amount": 79.97, "currency": "UAH", "valueAddedTaxIncluded": True},
             "relatedItem": related_item}
        ]}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Total amount can't be greater than bid.lotValue.value.amount",
            }
        ],
    )


def four_contracts_one_unsuccessful(self):
    response = self.app.get("/tenders/{}/agreements".format(self.tender_id))
    agreement = response.json["data"][0]
    self.assertEqual(agreement["status"], "pending")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    self.assertEqual(tender["status"], "active.awarded")

    # Fill 3 unitPrice.value.amount for all contracts in agreement
    response = self.app.get("/tenders/{}/agreements/{}/contracts".format(self.tender_id, self.agreement_id))
    contracts = response.json["data"]
    for contract in contracts[:-1]:
        unit_prices = contract["unitPrices"]
        for unit_price in unit_prices:
            unit_price["value"]["amount"] = 60
        response = self.app.patch_json(
            "/tenders/{}/agreements/{}/contracts/{}?acc_token={}".format(
                self.tender_id, self.agreement_id, contract["id"], self.tender_token
            ),
            {"data": {"unitPrices": unit_prices}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active")

    # Set last contract to unsuccessful
    response = self.app.patch_json(
        "/tenders/{}/agreements/{}/contracts/{}?acc_token={}".format(
            self.tender_id, self.agreement_id, contracts[-1]["id"], self.tender_token
        ),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")

    tender = self.mongodb.tenders.get(self.tender_id)
    tender["contractPeriod"]["startDate"] = (
        datetime.now() - CLARIFICATIONS_UNTIL_PERIOD - timedelta(days=1)
    ).isoformat()
    tender["contractPeriod"]["clarificationsUntil"] = (datetime.now() - timedelta(days=1)).isoformat()
    self.mongodb.tenders.save(tender)

    response = self.app.patch_json(
        "/tenders/{}/agreements/{}?acc_token={}".format(self.tender_id, self.agreement_id, self.tender_token),
        {"data": {"status": "active", "period": test_tender_cfaua_agreement_period}},
    )
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    self.assertEqual(tender["status"], "complete")
    self.assertEqual(len([c for c in tender["agreements"][0]["contracts"] if c["status"] == "active"]), 3)
    self.assertEqual(len([c for c in tender["agreements"][0]["contracts"] if c["status"] == "unsuccessful"]), 1)

    for unit_price in tender["agreements"][0]["contracts"][-1]["unitPrices"]:
        self.assertNotIn("amount", unit_price["value"])
