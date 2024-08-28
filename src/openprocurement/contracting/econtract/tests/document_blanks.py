from copy import deepcopy

from openprocurement.api.utils import get_now
from openprocurement.contracting.econtract.tests.data import test_signer_info
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_organization,
)
from openprocurement.tender.limited.tests.base import (
    test_tender_reporting_config,
    test_tender_reporting_data,
)


def patch_contract_document(self):
    response = self.app.put_json(
        f"/contracts/{self.contract_id}/suppliers/signer_info?acc_token={self.initial_data['bid_token']}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.put_json(
        f"/contracts/{self.contract_id}/buyer/signer_info?acc_token={self.contract_token}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={self.contract_token}",
        {
            "data": {
                "status": "active",
                "contractNumber": "123",
                "period": {
                    "startDate": "2016-03-18T18:47:47.155143+02:00",
                    "endDate": "2016-05-18T18:47:47.155143+02:00",
                },
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn(response.json["data"]["status"], "active")
    self.assertIn("signerInfo", response.json["data"]["buyer"])
    self.assertIn("signerInfo", response.json["data"]["suppliers"][0])

    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
        {
            "data": {
                "title": "укр.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.assertEqual("укр.doc", response.json["data"]["title"])
    self.assertEqual(response.json["data"]["documentOf"], "contract")
    self.assertNotIn("documentType", response.json["data"])

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/documents/{doc_id}?acc_token={self.contract_token}",
        {"data": {"description": "document description", "documentType": "notice"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertIn("documentType", response.json["data"])
    self.assertEqual(response.json["data"]["documentType"], "notice")

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/documents/{doc_id}?acc_token={self.contract_token}",
        {"data": {"documentType": None}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertNotIn("documentType", response.json["data"])

    response = self.app.get("/contracts/{}/documents/{}".format(self.contract_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("document description", response.json["data"]["description"])

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={self.contract_token}",
        {"data": {"status": "terminated", "amountPaid": {"amount": 100, "amountNet": 90}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "terminated")

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/documents/{doc_id}?acc_token={self.contract_token}",
        {"data": {"description": "document description X"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't update document in current (terminated) contract status",
                "location": "body",
                "name": "data",
            }
        ],
    )


def contract_change_document(self):
    response = self.app.put_json(
        f"/contracts/{self.contract_id}/suppliers/signer_info?acc_token={self.initial_data['bid_token']}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.put_json(
        f"/contracts/{self.contract_id}/buyer/signer_info?acc_token={self.contract_token}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={self.contract_token}",
        {
            "data": {
                "status": "active",
                "contractNumber": "123",
                "period": {
                    "startDate": "2016-03-18T18:47:47.155143+02:00",
                    "endDate": "2016-05-18T18:47:47.155143+02:00",
                },
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn(response.json["data"]["status"], "active")
    self.assertIn("signerInfo", response.json["data"]["buyer"])
    self.assertIn("signerInfo", response.json["data"]["suppliers"][0])

    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
        {
            "data": {
                "title": "укр.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.assertEqual("укр.doc", response.json["data"]["title"])
    self.assertEqual(response.json["data"]["documentOf"], "contract")
    self.assertNotIn("documentType", response.json["data"])

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/documents/{doc_id}?acc_token={self.contract_token}",
        {"data": {"documentOf": "change", "relatedItem": "1234" * 8}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "relatedItem", "description": ["relatedItem should be one of changes"]}],
    )

    response = self.app.post_json(
        f"/contracts/{self.contract_id}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationale_en": "change cause en",
                "rationaleTypes": ["priceReduction"],
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    change = response.json["data"]

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/documents/{doc_id}?acc_token={self.contract_token}",
        {"data": {"documentOf": "change", "relatedItem": change["id"]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual(response.json["data"]["documentOf"], "change")
    self.assertEqual(response.json["data"]["relatedItem"], change["id"])

    response = self.app.put_json(
        f"/contracts/{self.contract_id}/documents/{doc_id}?acc_token={self.contract_token}",
        {
            "data": {
                "title": "укр.doc",
                "url": self.generate_docservice_url("1" * 32),
                "hash": "md5:" + "1" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/changes/{change['id']}?acc_token={self.contract_token}",
        {"data": {"status": "active", "dateSigned": get_now().isoformat()}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
        {
            "data": {
                "title": "укр2.doc",
                "url": self.generate_docservice_url("2" * 32),
                "hash": "md5:" + "2" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    doc_id = response.json["data"]["id"]

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/documents/{doc_id}?acc_token={self.contract_token}",
        {"data": {"documentOf": "change", "relatedItem": change["id"]}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Can't add document to 'active' change"}],
    )


def limited_contract_confidential_document(self):
    tender_data = deepcopy(test_tender_reporting_data)
    tender_data["cause"] = "UZ"
    response = self.app.post_json("/tenders", {"data": tender_data, "config": test_tender_reporting_config})
    tender = response.json["data"]
    tender_id = tender["id"]
    tender_token = response.json["access"]["token"]
    # activate tender
    self.app.patch_json(f"/tenders/{tender_id}?acc_token={tender_token}", {"data": {"status": "active"}})
    # post award
    response = self.app.post_json(
        f"/tenders/{tender_id}/awards?acc_token={tender_token}",
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "subcontractingDetails": "Details",
                "status": "pending",
                "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False},
            }
        },
    )
    award_id = response.json["data"]["id"]
    # activate winner
    self.app.patch_json(
        f"/tenders/{tender_id}/awards/{award_id}?acc_token={tender_token}", {"data": {"status": "active"}}
    )
    response = self.app.get(f"/tenders/{tender_id}/contracts")
    contract_id = response.json["data"][0]["id"]

    response = self.app.patch_json(
        f"/contracts/{contract_id}/credentials?acc_token={tender_token}",
        {"data": {}},
    )
    contract_token = response.json["access"]["token"]

    request_data = {
        "title": "name.doc",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/msword",
        "confidentiality": "true",
    }

    # rogue value
    response = self.app.post_json(
        f"/contracts/{contract_id}/documents?acc_token={tender_token}",
        {"data": request_data},
        status=422,
    )
    self.assertEqual(
        response.json,
        {
            "status": "error",
            "errors": [
                {
                    "location": "body",
                    "name": "confidentiality",
                    "description": ["Value must be one of ['public', 'buyerOnly']."],
                }
            ],
        },
    )

    # add doc without documentType
    request_data["confidentiality"] = "buyerOnly"
    request_data["confidentialityRationale"] = f"{'a' * 30}"
    response = self.app.post_json(
        f"/contracts/{contract_id}/documents?acc_token={tender_token}",
        {"data": request_data},
        status=422,
    )
    self.assertEqual(
        response.json,
        {
            "status": "error",
            "errors": [{"location": "body", "name": "confidentiality", "description": "Document should be public"}],
        },
    )
    request_data["confidentiality"] = "public"
    del request_data["confidentialityRationale"]
    response = self.app.post_json(
        f"/contracts/{contract_id}/documents?acc_token={tender_token}",
        {"data": request_data},
        status=201,
    )
    doc_id_1 = response.json["data"]["id"]
    self.assertEqual(response.json["data"]["confidentiality"], "public")

    # add doc with confidential documentType
    request_data["documentType"] = "contractAnnexe"
    response = self.app.post_json(
        f"/contracts/{contract_id}/documents?acc_token={tender_token}",
        {"data": request_data},
        status=422,
    )
    self.assertEqual(
        response.json,
        {
            "status": "error",
            "errors": [
                {"location": "body", "name": "confidentiality", "description": "Document should be confidential"}
            ],
        },
    )
    # post confidential doc without rationale
    request_data["confidentiality"] = "buyerOnly"
    response = self.app.post_json(
        f"/contracts/{contract_id}/documents?acc_token={tender_token}",
        {"data": request_data},
        status=422,
    )
    self.assertEqual(
        response.json,
        {
            "status": "error",
            "errors": [
                {
                    "location": "body",
                    "name": "confidentialityRationale",
                    "description": ["confidentialityRationale is required"],
                }
            ],
        },
    )
    request_data["confidentialityRationale"] = "coz it is hidden"
    response = self.app.post_json(
        f"/contracts/{contract_id}/documents?acc_token={tender_token}",
        {"data": request_data},
        status=422,
    )
    self.assertEqual(
        response.json,
        {
            "status": "error",
            "errors": [
                {
                    "location": "body",
                    "name": "confidentialityRationale",
                    "description": ["confidentialityRationale should contain at least 30 characters"],
                }
            ],
        },
    )
    request_data["confidentialityRationale"] = "coz it is hidden because of the law"
    response = self.app.post_json(
        f"/contracts/{contract_id}/documents?acc_token={tender_token}",
        {"data": request_data},
        status=201,
    )
    doc_id_2 = response.json["data"]["id"]
    self.assertEqual(response.json["data"]["confidentiality"], "buyerOnly")

    # get list as tender owner
    response = self.app.get(f"/contracts/{contract_id}/documents?acc_token={tender_token}")
    self.assertEqual(len(response.json["data"]), 2)
    for doc in response.json["data"]:
        self.assertIn("url", doc)

    # get list as contract owner
    response = self.app.get(f"/contracts/{contract_id}/documents?acc_token={contract_token}")
    self.assertEqual(len(response.json["data"]), 2)
    for doc in response.json["data"]:
        self.assertIn("url", doc)

    # get list as public
    response = self.app.get(f"/contracts/{contract_id}/documents")
    self.assertEqual(len(response.json["data"]), 2)
    for doc in response.json["data"]:
        if doc["confidentiality"] == "buyerOnly":
            self.assertNotIn("url", doc)
        else:
            self.assertIn("url", doc)

    # get directly as tender owner
    response = self.app.get(f"/contracts/{contract_id}/documents/{doc_id_2}?acc_token={tender_token}")
    self.assertIn("url", response.json["data"])

    # get directly as public
    response = self.app.get(f"/contracts/{contract_id}/documents/{doc_id_2}")
    self.assertNotIn("url", response.json["data"])

    # download as tender owner
    response = self.app.get(
        f"/contracts/{contract_id}/documents/{doc_id_2}?acc_token={tender_token}&download=1",
    )
    self.assertEqual(response.status_code, 302)
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertIn("Expires=", response.location)

    # download as tender public
    response = self.app.get(
        f"/contracts/{contract_id}/documents/{doc_id_2}?download=1",
        status=403,
    )
    self.assertEqual(
        response.json,
        {
            "status": "error",
            "errors": [{"location": "body", "name": "data", "description": "Document download forbidden."}],
        },
    )

    # patch first doc documentType to confidential
    self.app.patch_json(
        f"/contracts/{contract_id}/documents/{doc_id_1}?acc_token={tender_token}",
        {
            "data": {
                "documentType": "contractSigned",
                "confidentiality": "buyerOnly",
                "confidentialityRationale": f"{'a' * 30}",
            }
        },
    )
    # get directly as tender owner
    response = self.app.get(f"/contracts/{contract_id}/documents/{doc_id_1}?acc_token={tender_token}")
    self.assertIn("url", response.json["data"])

    # get directly as public
    response = self.app.get(f"/contracts/{contract_id}/documents/{doc_id_1}")
    self.assertNotIn("url", response.json["data"])

    # put second doc documentOf to non confidential
    request_data.update(
        {
            "documentOf": "tender",
            "confidentiality": "public",
        }
    )

    self.app.put_json(
        f"/contracts/{contract_id}/documents/{doc_id_2}?acc_token={tender_token}",
        {"data": request_data},
    )
    # get directly as tender owner
    response = self.app.get(f"/contracts/{contract_id}/documents/{doc_id_2}?acc_token={tender_token}")
    self.assertIn("url", response.json["data"])

    # get directly as public
    response = self.app.get(f"/contracts/{contract_id}/documents/{doc_id_2}")
    self.assertIn("url", response.json["data"])
