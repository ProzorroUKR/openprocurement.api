from openprocurement.api.utils import get_now

from openprocurement.contracting.econtract.tests.data import test_signer_info


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
        f"/contracts/{self.contract_id}?acc_token={self.contract_token}", {"data": {"status": "active"}}
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
        f"/contracts/{self.contract_id}?acc_token={self.contract_token}", {"data": {"status": "active"}}
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
                "title": "укр2.doc",
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
