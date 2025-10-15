from uuid import uuid4

from openprocurement.contracting.core.procedure.models.access import AccessRole
from openprocurement.contracting.core.tests.utils import create_contract
from openprocurement.tender.core.tests.utils import change_auth


def get_access(self):
    response = self.app.get(
        f"/contracts/{self.contract_id}/access?acc_token={self.tender_token}",
        status=405,
    )
    self.assertEqual(response.status, "405 Method Not Allowed")


def generate_access(self):
    contract = self.mongodb.contracts.get(self.contract_id)
    for access in contract.get("access", []):
        for role in ("buyer", "supplier"):
            if role == access["role"]:
                self.assertNotIn("token", access)

    response = self.app.post_json(f"/contracts/{self.contract_id}/access", {"data": {}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "identifier", "description": ["This field is required."]}],
    )

    response = self.app.post_json(
        f"/contracts/{self.contract_id}/access",
        {"data": {"identifier": {"id": "12345678", "scheme": "UA-EDR"}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Invalid identifier"}],
    )

    with change_auth(self.app, ("Basic", ("brokerx", ""))):
        response = self.app.post_json(
            f"/contracts/{self.contract_id}/access",
            {"data": {"identifier": self.contract["buyer"]["identifier"]}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"],
            [{"location": "body", "name": "data", "description": "Owner mismatch"}],
        )

    response = self.app.post_json(
        f"/contracts/{self.contract_id}/access", {"data": {"identifier": self.contract["buyer"]["identifier"]}}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertIn("token", response.json["access"])
    self.assertIn("transfer", response.json["access"])
    buyer_token_1 = response.json["access"]["token"]

    # try to sign contract with tender_token (not permitted already)
    contract_sign_data = {
        "documentType": "contractSignature",
        "title": "sign.p7s",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/pkcs7-signature",
    }
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.tender_token}",
        {"data": contract_sign_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")

    contract = self.mongodb.contracts.get(self.contract_id)
    buyer_access = None
    for access in contract.get("access", []):
        for role in ("tender", "contract"):
            self.assertNotEqual(access["role"], role)
        if access["role"] == "buyer":
            buyer_access = access
    self.assertNotEqual(buyer_access, None)
    self.assertEqual(contract["owner"], buyer_access["owner"])
    self.assertIn("token", buyer_access)

    # try to sign contract with buyer_token_1
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={buyer_token_1}",
        {"data": contract_sign_data},
    )
    doc_id = response.json["data"]["id"]
    self.assertEqual(response.status, "201 Created")

    # try to regenerate token after successful submission of contract token
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/access",
        {"data": {"identifier": self.contract["buyer"]["identifier"]}},
    )
    buyer_token_2 = response.json["access"]["token"]

    # try to update contract with buyer_token
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/cancellations?acc_token={buyer_token_1}",
        {"data": {"reasonType": "requiresChanges", "reason": "want to change info"}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [{'location': 'url', 'name': 'permission', 'description': 'Forbidden'}],
    )

    # try to patch contract with buyer_token_2
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/cancellations?acc_token={buyer_token_2}",
        {"data": {"reasonType": "requiresChanges", "reason": "want to change info"}},
    )
    self.assertEqual(response.status, "201 Created")

    # as we cancel contract before
    contract_doc = self.mongodb.contracts.get(self.contract_id)
    contract_doc["status"] = "pending"
    contract_doc["cancellations"] = []
    self.mongodb.contracts.save(contract_doc)

    # set bid owner
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/access", {"data": {"identifier": self.contract["suppliers"][0]["identifier"]}}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertIn("token", response.json["access"])
    self.assertNotIn("transfer", response.json["access"])

    supplier_token = response.json["access"]["token"]

    contract = self.mongodb.contracts.get(self.contract_id)

    supplier_access = None
    for access in contract.get("access", []):
        for role in ("bid",):
            self.assertNotEqual(access["role"], role)
        if access["role"] == "supplier":
            supplier_access = access
    self.assertNotEqual(supplier_access, None)
    self.assertIn("token", supplier_access)

    # try to sign contract with supplier_token
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={supplier_token}",
        {"data": contract_sign_data},
    )
    self.assertEqual(response.status, "201 Created")

    # create contract without EDO platform (old flow)
    contract = self.initial_contract_data
    contract.update(
        {
            "tender_id": self.tender_id,
            "access": [
                {"token": self.bid_token, "owner": "broker", "role": AccessRole.BID},
                {
                    "token": self.tender_document["owner_token"],
                    "owner": self.tender_document["owner"],
                    "role": AccessRole.TENDER,
                },
            ],
        }
    )
    contract_id = contract["id"] = uuid4().hex
    contract = create_contract(self, contract)

    # try to generate access
    response = self.app.post_json(
        f"/contracts/{contract_id}/access",
        {"data": {"identifier": contract["buyer"]["identifier"]}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")  # resource not found for not electronic contract
