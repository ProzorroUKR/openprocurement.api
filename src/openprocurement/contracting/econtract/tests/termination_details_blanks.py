from unittest.mock import patch

COMPLETED_TERMINATION_DETAILS = {
    "reasonType": "completed",
    "reason": "all obligations fulfilled",
    "amountPaid": {"amount": 100, "currency": "UAH", "amountNet": 100, "valueAddedTaxIncluded": False},
}

DISRUPTED_TERMINATION_DETAILS = {
    "reasonType": "disrupted",
    "reason": "terminated by mutual agreement",
    "amountPaid": {"amount": 50, "currency": "UAH", "amountNet": 50, "valueAddedTaxIncluded": False},
}

SIGN_DATA = {
    "documentType": "terminationReport",
    "title": "sign.p7s",
    "format": "application/pkcs7-signature",
}


def patch_termination_details_buyer_only(self):
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.supplier_token}",
        {"data": {"terminationDetails": COMPLETED_TERMINATION_DETAILS}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{"location": "url", "name": "permission", "description": "Forbidden"}],
    )


def patch_termination_details_draft(self):
    # touching reasonType without the rest of the required data fails and is not persisted
    # `reason` is not required for `completed`, so the next missing field is `amountPaid`
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": {"reasonType": "completed"}}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "terminationDetails",
                "description": "amountPaid is required to activate terminationDetails",
            }
        ],
    )
    response = self.app.get(f"/contracts/{self.contract_id}?acc_token={self.contract_token}")
    self.assertNotIn("terminationDetails", response.json["data"])

    # `reason` is required for `disrupted`
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {
            "data": {
                "terminationDetails": {
                    "reasonType": "disrupted",
                    "amountPaid": {
                        "amount": 50,
                        "currency": "UAH",
                        "amountNet": 50,
                        "valueAddedTaxIncluded": False,
                    },
                }
            }
        },
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "terminationDetails",
                "description": "reason is required to activate terminationDetails",
            }
        ],
    )

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": COMPLETED_TERMINATION_DETAILS}},
    )
    self.assertEqual(response.status, "200 OK")
    termination_details = response.json["data"]
    self.assertEqual(termination_details["status"], "draft")
    self.assertEqual(termination_details["reasonType"], "completed")
    self.assertIn("dateCreated", termination_details)
    self.assertNotIn("datePublished", termination_details)


def patch_termination_details_pending_change_forbidden(self):
    pdf_data = {
        "url": self.generate_docservice_url(),
        "format": "application/pdf",
        "hash": "md5:" + "0" * 32,
        "title": "contract_change.pdf",
    }
    upload_patch = patch(
        "openprocurement.tender.core.procedure.contracting.upload_contract_change_pdf",
        return_value={"data": pdf_data},
    )
    upload_patch.start()
    self.addCleanup(upload_patch.stop)

    self.app.post_json(
        f"/contracts/{self.contract_id}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "Опис причини змін контракту",
                "rationale_en": "Contract change cause",
                "modifications": {"title": "New title of contract"},
                "rationaleTypes": ["priceReductionWithoutQuantity"],
            }
        },
    )

    # an empty patch doesn't touch terminationDetails, so the pending change check
    # must not trigger for it
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": COMPLETED_TERMINATION_DETAILS}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "terminationDetails",
                "description": "Can't create terminationDetails while contract has a pending change",
            }
        ],
    )
    response = self.app.get(f"/contracts/{self.contract_id}?acc_token={self.contract_token}")
    self.assertNotIn("terminationDetails", response.json["data"])


def activate_termination_details_without_required_fields(self):
    # no PATCH was ever made yet, so terminationDetails doesn't exist at all
    sign_data = dict(SIGN_DATA, url=self.generate_docservice_url(), hash="md5:" + "0" * 32)
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/termination_details/documents?acc_token={self.contract_token}",
        {"data": sign_data},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")


def upload_termination_signature_requires_buyer(self):
    self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": COMPLETED_TERMINATION_DETAILS}},
    )
    sign_data = dict(SIGN_DATA, url=self.generate_docservice_url(), hash="md5:" + "0" * 32)
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/termination_details/documents?acc_token={self.supplier_token}",
        {"data": sign_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")


def upload_termination_signature_wrong_document_type(self):
    self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": COMPLETED_TERMINATION_DETAILS}},
    )
    sign_data = {
        "documentType": "contractSignature",
        "title": "sign.p7s",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/pkcs7-signature",
    }
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/termination_details/documents?acc_token={self.contract_token}",
        {"data": sign_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")


def activate_termination_details_completed(self):
    self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": COMPLETED_TERMINATION_DETAILS}},
    )
    sign_data = dict(SIGN_DATA, url=self.generate_docservice_url(), hash="md5:" + "0" * 32)
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/termination_details/documents?acc_token={self.contract_token}",
        {"data": sign_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["author"], "buyer")

    response = self.app.get(f"/contracts/{self.contract_id}?acc_token={self.contract_token}")
    termination_details = response.json["data"]["terminationDetails"]
    self.assertEqual(termination_details["status"], "active")
    self.assertIn("datePublished", termination_details)
    self.assertEqual(len(termination_details["documents"]), 1)
    self.assertEqual(response.json["data"]["status"], "terminated")

    # immutable once published
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": {"reason": "changed my mind"}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")


def get_termination_details(self):
    response = self.app.get(
        f"/contracts/{self.contract_id}/termination_details",
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")

    self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": COMPLETED_TERMINATION_DETAILS}},
    )
    response = self.app.get(f"/contracts/{self.contract_id}/termination_details")
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("context", response.json)
    termination_details = response.json["data"]
    self.assertEqual(termination_details["status"], "draft")
    self.assertEqual(termination_details["reasonType"], "completed")
    self.assertNotIn("documents", termination_details)


def get_termination_details_context(self):
    self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": COMPLETED_TERMINATION_DETAILS}},
    )
    sign_data = dict(SIGN_DATA, url=self.generate_docservice_url(), hash="md5:" + "0" * 32)
    self.app.post_json(
        f"/contracts/{self.contract_id}/termination_details/documents?acc_token={self.contract_token}",
        {"data": sign_data},
    )

    response = self.app.get(f"/contracts/{self.contract_id}/termination_details?opt_context=true")
    self.assertEqual(response.status, "200 OK")
    termination_details = response.json["data"]
    self.assertEqual(termination_details["status"], "active")
    self.assertEqual(len(termination_details["documents"]), 1)
    document = termination_details["documents"][0]
    self.assertEqual(document["documentType"], "terminationReport")
    self.assertEqual(document["title"], "sign.p7s")

    context = response.json["context"]
    self.assertIn("id", context["contract"])
    self.assertIn("items", context["contract"])
    self.assertEqual(context["contract"]["id"], self.contract_id)
    self.assertEqual(context["contract"]["status"], "terminated")


STATE_MODULE = "openprocurement.contracting.econtract.procedure.state.contract_termination_details_document"


@patch(f"{STATE_MODULE}.SIGNATURE_VERIFICATION_ENABLED", True)
@patch(f"{STATE_MODULE}.load_document_content")
@patch(f"{STATE_MODULE}.verify_signature_apisign")
def activate_termination_details_signature_verified(self, verify_signature_apisign_mock, load_document_content_mock):
    load_document_content_mock.return_value = b"signature-bytes"
    verify_signature_apisign_mock.return_value = {
        "sign_info": {"pdwSignType": 16},
        "cert_info": {"dwPublicKeyType": 1},
    }

    self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": COMPLETED_TERMINATION_DETAILS}},
    )
    sign_data = dict(SIGN_DATA, url=self.generate_docservice_url(), hash="md5:" + "0" * 32)
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/termination_details/documents?acc_token={self.contract_token}",
        {"data": sign_data},
    )
    self.assertEqual(response.status, "201 Created")

    verify_signature_apisign_mock.assert_called_once()
    content, signature = verify_signature_apisign_mock.call_args.args
    self.assertIsInstance(content, bytes)
    self.assertEqual(signature, b"signature-bytes")

    response = self.app.get(f"/contracts/{self.contract_id}?acc_token={self.contract_token}")
    termination_details = response.json["data"]["terminationDetails"]
    self.assertEqual(termination_details["status"], "active")
    self.assertEqual(response.json["data"]["status"], "terminated")


@patch(f"{STATE_MODULE}.SIGNATURE_VERIFICATION_ENABLED", True)
@patch(f"{STATE_MODULE}.load_document_content")
@patch(f"{STATE_MODULE}.verify_signature_apisign")
def activate_termination_details_signature_invalid_type(
    self, verify_signature_apisign_mock, load_document_content_mock
):
    load_document_content_mock.return_value = b"signature-bytes"
    verify_signature_apisign_mock.return_value = {
        "sign_info": {"pdwSignType": 1},
        "cert_info": {"dwPublicKeyType": 1},
    }

    self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": COMPLETED_TERMINATION_DETAILS}},
    )
    sign_data = dict(SIGN_DATA, url=self.generate_docservice_url(), hash="md5:" + "0" * 32)
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/termination_details/documents?acc_token={self.contract_token}",
        {"data": sign_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertIn("Invalid signature type", response.json["errors"][0]["description"])

    response = self.app.get(f"/contracts/{self.contract_id}?acc_token={self.contract_token}")
    self.assertEqual(response.json["data"]["terminationDetails"]["status"], "draft")


@patch(f"{STATE_MODULE}.SIGNATURE_VERIFICATION_ENABLED", True)
@patch(f"{STATE_MODULE}.load_document_content")
@patch(f"{STATE_MODULE}.verify_signature_apisign")
def activate_termination_details_signature_invalid_cert(
    self, verify_signature_apisign_mock, load_document_content_mock
):
    load_document_content_mock.return_value = b"signature-bytes"
    verify_signature_apisign_mock.return_value = {
        "sign_info": {"pdwSignType": 16},
        "cert_info": {"dwPublicKeyType": 2},
    }

    self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": COMPLETED_TERMINATION_DETAILS}},
    )
    sign_data = dict(SIGN_DATA, url=self.generate_docservice_url(), hash="md5:" + "0" * 32)
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/termination_details/documents?acc_token={self.contract_token}",
        {"data": sign_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertIn("Invalid certificate key type", response.json["errors"][0]["description"])


def delete_termination_details_not_found(self):
    response = self.app.delete(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")


def delete_termination_details_buyer_only(self):
    self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": COMPLETED_TERMINATION_DETAILS}},
    )
    response = self.app.delete(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.supplier_token}",
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{"location": "url", "name": "permission", "description": "Forbidden"}],
    )


def delete_termination_details_draft(self):
    self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": COMPLETED_TERMINATION_DETAILS}},
    )
    response = self.app.delete(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["reasonType"], "completed")

    response = self.app.get(
        f"/contracts/{self.contract_id}/termination_details",
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")

    response = self.app.get(f"/contracts/{self.contract_id}?acc_token={self.contract_token}")
    self.assertNotIn("terminationDetails", response.json["data"])


def delete_termination_details_after_active_forbidden(self):
    self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": COMPLETED_TERMINATION_DETAILS}},
    )
    sign_data = dict(SIGN_DATA, url=self.generate_docservice_url(), hash="md5:" + "0" * 32)
    self.app.post_json(
        f"/contracts/{self.contract_id}/termination_details/documents?acc_token={self.contract_token}",
        {"data": sign_data},
    )

    response = self.app.delete(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can't update contract in current (terminated) status",
            }
        ],
    )


def activate_termination_details_disrupted_amount_exceeds_value(self):
    # for reasonType `disrupted`, amountPaid must not exceed the contract value
    # (checked eagerly, not only at signing time)
    contract = self.app.get(f"/contracts/{self.contract_id}").json["data"]
    value = contract["value"]

    too_much = dict(DISRUPTED_TERMINATION_DETAILS)
    too_much["amountPaid"] = {
        "amount": value["amount"] + 1,
        "amountNet": value["amount"] + 1,
        "currency": value["currency"],
        "valueAddedTaxIncluded": False,
    }
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": too_much}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "terminationDetails",
                "description": "terminationDetails.amountPaid.amount must not exceed contract value.amount",
            }
        ],
    )

    wrong_currency = dict(DISRUPTED_TERMINATION_DETAILS)
    wrong_currency["amountPaid"] = {"amount": 1, "amountNet": 1, "currency": "EUR", "valueAddedTaxIncluded": False}
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": wrong_currency}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "terminationDetails",
                "description": "currency of amountPaid should be identical to currency of value of contract",
            }
        ],
    )


def activate_termination_details_completed_amount_paid_zero(self):
    zero_amount = dict(COMPLETED_TERMINATION_DETAILS)
    zero_amount["amountPaid"] = {"amount": 0, "amountNet": 0, "currency": "UAH", "valueAddedTaxIncluded": False}
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": zero_amount}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "terminationDetails",
                "description": "terminationDetails.amountPaid.amount must be greater than 0",
            }
        ],
    )

    zero_amount_disrupted = dict(DISRUPTED_TERMINATION_DETAILS)
    zero_amount_disrupted["amountPaid"] = {
        "amount": 0,
        "amountNet": 0,
        "currency": "UAH",
        "valueAddedTaxIncluded": False,
    }
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": zero_amount_disrupted}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["amountPaid"]["amount"], 0)


def activate_termination_details_reason_required(self):
    without_reason = dict(COMPLETED_TERMINATION_DETAILS)
    del without_reason["reason"]
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": without_reason}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("reason", response.json["data"])

    self.app.delete(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
    )
    without_reason = dict(DISRUPTED_TERMINATION_DETAILS)
    del without_reason["reason"]
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": without_reason}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "terminationDetails",
                "description": "reason is required to activate terminationDetails",
            }
        ],
    )
