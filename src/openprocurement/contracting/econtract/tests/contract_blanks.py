from copy import deepcopy
from unittest.mock import patch
from uuid import uuid4

from openprocurement.api.constants import MILESTONE_CODES, MILESTONE_TITLES
from openprocurement.contracting.core.tests.data import test_signer_info
from openprocurement.tender.core.tests.utils import change_auth


def contract_activate(self):
    response = self.app.get(f"/contracts/{self.contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.contract_token}",
        {"data": {"status": "active"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "signerInfo field for buyer and suppliers is required for contract in `active` status",
            }
        ],
    )

    response = self.app.put_json(
        f"/contracts/{self.contract_id}/buyer/signer_info?acc_token={self.contract_token}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.put_json(
        f"/contracts/{self.contract_id}/suppliers/signer_info?acc_token={self.bid_token}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={self.contract_token}",
        {"data": {"status": "active"}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "period is required for contract in `active` status",
    )

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={self.contract_token}",
        {
            "data": {
                "status": "active",
                "period": {
                    "startDate": "2016-03-18T18:47:47.155143+02:00",
                    "endDate": "2016-05-18T18:47:47.155143+02:00",
                },
            }
        },
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "contractNumber is required for contract in `active` status",
    )

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={self.contract_token}",
        {
            "data": {
                "contractNumber": "123",
                "period": {
                    "startDate": "2016-03-18T18:47:47.155143+02:00",
                    "endDate": "2016-05-18T18:47:47.155143+02:00",
                },
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    # try to activate contract
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.contract_token}",
        {"data": {"status": "active"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "contractSignature document type for all participants is required for contract in `active` status",
            }
        ],
    )

    # add signature only for buyer
    contract_sign_data = {
        "documentType": "contractSignature",
        "title": "sign.p7s",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/pkcs7-signature",
    }
    self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
        {"data": contract_sign_data},
    )

    # try to activate again
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.contract_token}",
        {"data": {"status": "active"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "contractSignature document type for all participants is required f"
                "or contract in `active` status",
            }
        ],
    )

    # add signature for supplier
    self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.bid_token}",
        {"data": contract_sign_data},
    )

    # it is automatically activated after second signature
    response = self.app.get(f"/contracts/{self.contract['id']}?acc_token={self.contract_token}")
    self.assertEqual(response.json["data"]["status"], "active")


def update_pending_contract_forbidden(self):
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={self.contract_token}",
        {"data": {"title": "new contract"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can't update contract in current (pending) status",
            }
        ],
    )


def post_new_version_of_contract(self):
    response = self.app.get(f"/contracts/{self.contract_id}")
    initial_contract_data = response.json["data"]
    contract_data = deepcopy(initial_contract_data)
    del contract_data["dateCreated"]
    del contract_data["dateModified"]
    del contract_data["id"]

    with change_auth(self.app, ("Basic", ("brokerx", ""))):
        response = self.app.post_json(
            "/contracts",
            {"data": contract_data},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "url",
                    "name": "accreditation",
                    "description": "Broker Accreditation level does not permit contract creation",
                }
            ],
        )
    # invalid tender id
    contract_data["tender_id"] = uuid4().hex
    response = self.app.post_json(
        "/contracts",
        {"data": contract_data},
        status=404,
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "url", "name": "tender_id", "description": "Not Found"}],
    )

    contract_data["tender_id"] = self.tender_id
    response = self.app.post_json(
        "/contracts",
        {"data": contract_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Previous version of pending contract with cancellations not found",
            }
        ],
    )

    # add cancellation by supplier
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/cancellations?acc_token={self.supplier_token}",
        {"data": {"reasonType": "requiresChanges", "reason": "want to change info"}},
    )
    self.assertEqual(response.status, "201 Created")

    # try to create contract without token
    response = self.app.post_json(
        "/contracts",
        {"data": contract_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Role isn't found, check auth and token"}],
    )

    # try to change forbidden field
    contract_data["title_ru"] = "New contract"
    response = self.app.post_json(
        f"/contracts?acc_token={self.supplier_token}",
        {"data": contract_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Updated could be only ('items', 'value', 'period', 'title', 'title_en', 'description', 'description_en', 'dateSigned', 'milestones', 'suppliers') in contract, title_ru change forbidden",
            }
        ],
    )

    del contract_data["title_ru"]
    contract_data["items"][0]["deliveryDate"] = {
        "startDate": "2022-01-01",
    }
    contract_data.update(
        {
            "period": {
                "startDate": "2022-01-01",
                "endDate": "2026-01-01",
            },
        }
    )
    response = self.app.post_json(
        f"/contracts?acc_token={self.supplier_token}",
        {"data": contract_data},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Updated could be only ('unit', 'quantity') in item, deliveryDate change forbidden",
            }
        ],
    )

    contract_data["items"][0]["deliveryDate"] = initial_contract_data["items"][0]["deliveryDate"]
    contract_data["value"]["currency"] = "USD"
    response = self.app.post_json(
        f"/contracts?acc_token={self.supplier_token}",
        {"data": contract_data},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "value", "description": "Can't update currency for contract value"}],
    )

    contract_data["value"]["currency"] = "UAH"
    contract_data["value"]["amount"] = 100
    response = self.app.post_json(
        f"/contracts?acc_token={self.supplier_token}",
        {"data": contract_data},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "value",
                "description": "Amount should be equal or greater than amountNet and differ by no more than 20.0%",
            }
        ],
    )

    contract_data["value"] = deepcopy(initial_contract_data["value"])
    del contract_data["value"]["amountNet"]
    response = self.app.post_json(
        f"/contracts?acc_token={self.supplier_token}",
        {"data": contract_data},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "value", "description": {"amountNet": "This field is required."}}],
    )

    contract_data["value"]["amountNet"] = contract_data["value"]["amount"]
    contract_data["suppliers"][0]["name"] = "new name"
    response = self.app.post_json(
        f"/contracts?acc_token={self.supplier_token}",
        {"data": contract_data},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Updated could be only signerInfo in suppliers, name change forbidden",
            }
        ],
    )

    contract_data["suppliers"] = deepcopy(initial_contract_data["suppliers"])
    contract_data["suppliers"][0]["signerInfo"].update(
        {
            "email": "new@gmail.com",
            "name": "New supplier",
        }
    )
    contract_data["contractChangeRationaleTypes"] = {"test": "test"}
    pdf_data = {
        "url": self.generate_docservice_url(),
        "format": "application/pdf",
        "hash": "md5:" + "0" * 32,
        "title": "contract.pdf",
    }

    contract_data["value"]["amount"] = self.award["value"]["amount"]
    contract_data["value"]["amountNet"] = contract_data["value"]["amount"]

    with patch("openprocurement.tender.core.procedure.contracting.upload_contract_pdf") as mock_upload_contract_pdf:
        mock_upload_contract_pdf.return_value = {"data": pdf_data}
        response = self.app.post_json(
            f"/contracts?acc_token={self.supplier_token}",
            {"data": contract_data},
        )
        mock_upload_contract_pdf.assert_called_once()

    new_contract = response.json["data"]
    self.assertEqual(new_contract["status"], "pending")
    self.assertEqual(new_contract["author"], "supplier")
    self.assertEqual(new_contract["suppliers"][0]["signerInfo"]["email"], "new@gmail.com")
    self.assertEqual(
        new_contract["contractChangeRationaleTypes"], initial_contract_data["contractChangeRationaleTypes"]
    )

    self.assertIn("documents", new_contract)
    self.assertEqual(new_contract["documents"][0]["documentType"], "contractNotice")
    self.assertEqual(new_contract["documents"][0]["format"], pdf_data["format"])
    self.assertEqual(new_contract["documents"][0]["hash"], pdf_data["hash"])
    self.assertEqual(new_contract["documents"][0]["title"], pdf_data["title"])
    self.assertIn("url", new_contract["documents"][0])
    self.assertIn("datePublished", new_contract["documents"][0])
    self.assertIn("dateModified", new_contract["documents"][0])

    response = self.app.get(
        f"/tenders/{self.tender_id}/contracts",
    )
    self.assertEqual(len(response.json["data"]), 2)
    self.assertEqual(response.json["data"][0]["status"], "cancelled")
    self.assertEqual(response.json["data"][1]["status"], "pending")

    response = self.app.get(
        f"/contracts?acc_token={self.supplier_token}",
    )
    self.assertEqual(len(response.json["data"]), 2)

    response = self.app.get(
        f"/contracts/{self.contract_id}",
    )
    prev_contract = response.json["data"]
    self.assertEqual(prev_contract["status"], "cancelled")
    self.assertEqual(prev_contract["cancellations"][0]["status"], "active")

    response = self.app.get(
        f"/contracts/{new_contract['id']}",
    )
    new_contract = response.json["data"]
    self.assertEqual(new_contract["status"], "pending")
    self.assertNotEqual(prev_contract["contractID"], new_contract["contractID"])
    self.assertNotEqual(prev_contract["dateCreated"], new_contract["dateCreated"])


def contract_cancellation_via_award(self):
    response = self.app.get(f"/contracts/{self.contract_id}")
    initial_contract_data = response.json["data"]
    contract_data = deepcopy(initial_contract_data)
    del contract_data["dateCreated"]
    del contract_data["dateModified"]

    # add cancellation by supplier
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/cancellations?acc_token={self.supplier_token}",
        {"data": {"reasonType": "signingRefusal", "reason": "want to quid"}},
    )
    self.assertEqual(response.status, "201 Created")

    # try to create new version of contract
    contract_data["tender_id"] = self.tender_id
    response = self.app.post_json(
        f"/contracts?acc_token={self.contract_token}",
        {"data": contract_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "For contract with cancellation reason `signingRefusal` buyer should cancel the award.",
            }
        ],
    )
    response = self.app.get(f"/contracts/{self.contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/awards/{self.contract['awardID']}?acc_token={self.tender_token}",
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    response = self.app.get(f"/tenders/{self.tender_id}/contracts/{self.contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    response = self.app.get(f"/contracts/{self.contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    response = self.app.get(f"/contracts/{self.contract['id']}/cancellations")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"][0]["status"], "active")


change_contract_milestones_params = [
    (
        "financing milestones duration.days validation",
        [
            {
                "id": "0f15f4f3d94c4bb8aee50e28c4c2dbd7",
                "title": "signingTheContract",
                "type": "financing",
                "duration": {"days": 1500, "type": "banking"},
                "sequenceNumber": 1,
                "code": "prepayment",
                "percentage": 100,
            }
        ],
        422,
        lambda test_case, response: test_case.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "milestones",
                    "description": [{"duration": ["days shouldn't be more than 1000 for financing milestone"]}],
                }
            ],
        ),
    ),
    (
        "delivery milestones duration.days validation",
        [
            {
                "id": "0f15f4f3d94c4bb8aee50e28c4c2dbd7",
                "title": "signingTheContract",
                "type": "delivery",
                "duration": {"days": 1500, "type": "calendar"},
                "sequenceNumber": 1,
                "code": "standard",
                "percentage": 100,
            }
        ],
        422,
        lambda test_case, response: test_case.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "milestones",
                    "description": [{"duration": ["days shouldn't be more than 1000 for delivery milestone"]}],
                }
            ],
        ),
    ),
    (
        "milestones financing code validation",
        [
            {
                "id": "0f15f4f3d94c4bb8aee50e28c4c2dbd7",
                "title": "signingTheContract",
                "type": "financing",
                "duration": {"days": 2, "type": "banking"},
                "sequenceNumber": 1,
                "code": "test",
                "percentage": 100,
            }
        ],
        422,
        lambda test_case, response: test_case.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "milestones",
                    "description": [{"code": [f"Value must be one of {MILESTONE_CODES['financing']}"]}],
                }
            ],
        ),
    ),
    (
        "milestones delivery code validation",
        [
            {
                "id": "0f15f4f3d94c4bb8aee50e28c4c2dbd7",
                "title": "signingTheContract",
                "type": "delivery",
                "duration": {"days": 2, "type": "calendar"},
                "sequenceNumber": 1,
                "code": "test",
                "percentage": 100,
            }
        ],
        422,
        lambda test_case, response: test_case.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "milestones",
                    "description": [{"code": [f"Value must be one of {MILESTONE_CODES['delivery']}"]}],
                }
            ],
        ),
    ),
    (
        "milestones financing title validation",
        [
            {
                "id": "0f15f4f3d94c4bb8aee50e28c4c2dbd7",
                "title": "test",
                "type": "financing",
                "duration": {"days": 2, "type": "banking"},
                "sequenceNumber": 1,
                "code": "prepayment",
                "percentage": 100,
            }
        ],
        422,
        lambda test_case, response: test_case.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "milestones",
                    "description": [{"title": [f"Value must be one of {MILESTONE_TITLES['financing']}"]}],
                }
            ],
        ),
    ),
    (
        "milestones delivery title validation",
        [
            {
                "id": "0f15f4f3d94c4bb8aee50e28c4c2dbd7",
                "title": "test",
                "type": "delivery",
                "duration": {"days": 2, "type": "calendar"},
                "sequenceNumber": 1,
                "code": "standard",
                "percentage": 100,
            }
        ],
        422,
        lambda test_case, response: test_case.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "milestones",
                    "description": [{"title": [f"Value must be one of {MILESTONE_TITLES['delivery']}"]}],
                }
            ],
        ),
    ),
    (
        "milestones percentages validation",
        [
            {
                "id": "0f15f4f3d94c4bb8aee50e28c4c2dbd7",
                "title": "signingTheContract",
                "type": "financing",
                "duration": {"days": 2, "type": "banking"},
                "sequenceNumber": 1,
                "code": "prepayment",
                "percentage": 10,
            }
        ],
        422,
        lambda test_case, response: test_case.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "milestones",
                    "description": "Sum of the financing milestone percentages 10.0 is not equal 100.",
                }
            ],
        ),
    ),
    (
        "successful milestones post",
        [
            {
                "id": "0f15f4f3d94c4bb8aee50e28c4c2dbd7",
                "title": "signingTheContract",
                "type": "financing",
                "duration": {"days": 2, "type": "banking"},
                "sequenceNumber": 1,
                "code": "prepayment",
                "percentage": 100,
            }
        ],
        201,
        lambda test_case, response: test_case.assertCountEqual(
            response.json["data"]["milestones"],
            [
                {
                    "id": "0f15f4f3d94c4bb8aee50e28c4c2dbd7",
                    "title": "signingTheContract",
                    "type": "financing",
                    "duration": {"days": 2, "type": "banking"},
                    "sequenceNumber": 1,
                    "code": "prepayment",
                    "percentage": 100,
                    "status": "scheduled",
                }
            ],
        ),
    ),
    (
        "invalid sequenceNumber",
        [
            {
                "id": "0f15f4f3d94c4bb8aee50e28c4c2dbd7",
                "title": "signingTheContract",
                "type": "financing",
                "duration": {"days": 2, "type": "banking"},
                "sequenceNumber": 1,
                "code": "prepayment",
                "percentage": 100,
            },
            {
                "id": "a452fdca492b4fa6ab2ba7c871739a72",
                "title": "signingTheContract",
                "type": "delivery",
                "duration": {"days": 2, "type": "calendar"},
                "sequenceNumber": 0,
                "code": "standard",
                "percentage": 100,
            },
        ],
        422,
        lambda test_case, response: test_case.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "milestones",
                    "description": [
                        {"sequenceNumber": "Field should contain incrementing sequence numbers starting from 1"}
                    ],
                }
            ],
        ),
    ),
    (
        "valid sequenceNumber",
        [
            {
                "id": "0f15f4f3d94c4bb8aee50e28c4c2dbd7",
                "title": "signingTheContract",
                "type": "financing",
                "duration": {"days": 2, "type": "banking"},
                "sequenceNumber": 1,
                "code": "prepayment",
                "percentage": 100,
            },
            {
                "id": "a452fdca492b4fa6ab2ba7c871739a72",
                "title": "signingTheContract",
                "type": "delivery",
                "duration": {"days": 2, "type": "calendar"},
                "sequenceNumber": 2,
                "code": "standard",
                "percentage": 100,
            },
        ],
        201,
        lambda test_case, response: test_case.assertCountEqual(
            response.json["data"]["milestones"],
            [
                {
                    "id": "0f15f4f3d94c4bb8aee50e28c4c2dbd7",
                    "title": "signingTheContract",
                    "type": "financing",
                    "duration": {"days": 2, "type": "banking"},
                    "sequenceNumber": 1,
                    "code": "prepayment",
                    "percentage": 100,
                    "status": "scheduled",
                },
                {
                    "id": "a452fdca492b4fa6ab2ba7c871739a72",
                    "title": "signingTheContract",
                    "type": "delivery",
                    "duration": {"days": 2, "type": "calendar"},
                    "sequenceNumber": 2,
                    "code": "standard",
                    "percentage": 100,
                    "status": "scheduled",
                },
            ],
        ),
    ),
    (
        "empty milestones list",
        [],
        201,
        lambda test_case, response: test_case.assertNotIn("milestones", response.json["data"]),
    ),
]


def change_contract_milestones(self, _, milestones, resp_status, check_response):
    contract_data = deepcopy(self.contract)
    del contract_data["dateCreated"]
    del contract_data["dateModified"]

    # add cancellation by supplier
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/cancellations?acc_token={self.supplier_token}",
        {"data": {"reasonType": "requiresChanges", "reason": "want to change info"}},
        status=201,
    )
    self.assertEqual(response.status, "201 Created")

    pdf_data = {
        "url": self.generate_docservice_url(),
        "format": "application/pdf",
        "hash": "md5:" + "0" * 32,
        "title": "contract.pdf",
    }

    with patch(
        "openprocurement.tender.core.procedure.contracting.upload_contract_pdf", return_value={"data": pdf_data}
    ):
        response = self.app.post_json(
            f"/contracts?acc_token={self.supplier_token}",
            {"data": {**contract_data, "milestones": milestones}},
            status=resp_status,
        )

    check_response(self, response)
