from freezegun import freeze_time

from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.tender.openua.tests.bid_blanks import clean_requirement_responses

# TenderQualificationResourceTest


def post_tender_qualifications(self):
    response = self.app.post_json("/tenders/{}/qualifications".format(self.tender_id), {"data": {}}, status=405)
    self.assertEqual(response.status, "405 Method Not Allowed")

    data = {"bidID": "some_id", "status": "pending"}
    response = self.app.post_json("/tenders/{}/qualifications".format(self.tender_id), {"data": data}, status=405)
    self.assertEqual(response.status, "405 Method Not Allowed")

    data = {"bidID": "1234" * 8, "status": "pending", "id": "12345678123456781234567812345678"}
    response = self.app.post_json("/tenders/{}/qualifications".format(self.tender_id), {"data": data}, status=405)
    self.assertEqual(response.status, "405 Method Not Allowed")

    data = {"bidID": "1234" * 8, "status": "pending", "id": "12345678123456781234567812345678"}
    response = self.app.post_json(
        "/tenders/{}/qualifications/{}".format(self.tender_id, data["id"]), {"data": data}, status=405
    )
    self.assertEqual(response.status, "405 Method Not Allowed")

    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    qualifications = response.json["data"]
    data = {"bidID": "1234" * 8, "status": "pending", "id": qualifications[0]["id"]}
    response = self.app.post_json(
        "/tenders/{}/qualifications/{}".format(self.tender_id, qualifications[0]["id"]), {"data": data}, status=405
    )
    self.assertEqual(response.status, "405 Method Not Allowed")


def get_tender_qualifications_collection(self):
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    self.assertEqual(len(qualifications), self.min_bids_number)

    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    qualification_bid_ids = [q["bidID"] for q in qualifications]
    for bid in response.json["data"]:
        self.assertIn(bid["id"], qualification_bid_ids)
        qualification_bid_ids.remove(bid["id"])


def patch_tender_qualifications(self):
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    self.assertEqual(len(qualifications), self.min_bids_number)

    q1_id = qualifications[0]["id"]
    q2_id = qualifications[1]["id"]

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, q1_id, self.tender_token),
        {"data": {"title": "title", "description": "description", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["title"], "title")
    self.assertEqual(response.json["data"]["description"], "description")
    self.assertEqual(response.json["data"]["qualified"], True)
    self.assertEqual(response.json["data"]["eligible"], True)
    self.assertEqual(response.json["data"]["date"], qualifications[0]["date"])

    # first qualification manipulations
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, q1_id, self.tender_token),
        {
            "data": {
                "title": "title",
                "description": "description",
                "status": "active",
                "qualified": True,
                "eligible": True,
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertGreater(response.json["data"]["date"], qualifications[0]["date"])
    self.assertEqual(response.json["data"]["title"], "title")
    self.assertEqual(response.json["data"]["description"], "description")

    for status in ["pending", "unsuccessful"]:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, q1_id, self.tender_token),
            {"data": {"status": status}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.json["errors"][0]["description"], "Can't update qualification status")

    ## activequalification can be cancelled
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, q1_id, self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    ## cancelled status is terminated
    for status in ["pending", "active", "unsuccessful"]:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, q1_id, self.tender_token),
            {"data": {"status": status}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't update qualification in current cancelled qualification status",
        )

    # second qualification manipulations
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, q2_id, self.tender_token),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")

    for status in ["pending", "active"]:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, q2_id, self.tender_token),
            {"data": {"status": status, "qualified": True, "eligible": True}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.json["errors"][0]["description"], "Can't update qualification status")

    ## unsuccessful qualification can be cancelled
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, q2_id, self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    # list for new qualification
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    qualifications = response.json["data"]
    self.assertEqual(len(qualifications), self.min_bids_number + 2)
    q1 = qualifications[0]
    q3 = qualifications[self.min_bids_number]
    self.assertEqual(q1["bidID"], q3["bidID"])
    q2 = qualifications[1]
    q4 = qualifications[self.min_bids_number + 1]
    self.assertEqual(q2["bidID"], q4["bidID"])

    self.assertEqual(q3["status"], "pending")

    # cancel pending qualification
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, q3["id"], self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    # one more qualification should be generated
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    qualifications = response.json["data"]
    self.assertEqual(len(qualifications), self.min_bids_number + 3)
    self.assertEqual(q3["bidID"], qualifications[self.min_bids_number]["bidID"])
    # activate rest qualifications
    for q_id in (qualifications[self.min_bids_number + 1]["id"], qualifications[self.min_bids_number + 2]["id"]):
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, q_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active")


def get_tender_qualifications(self):
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.status, "200 OK")
    qualifications = response.json["data"]
    for qualification in qualifications:
        response = self.app.get(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token)
        )
        self.assertEqual(response.status, "200 OK")


def patch_tender_qualifications_after_status_change(self):
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.status, "200 OK")
    qualifications = response.json["data"]
    for qualification in qualifications:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
    self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
        {"data": {"status": "cancelled"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't update qualification in current (active.pre-qualification.stand-still) tender status",
                "location": "body",
                "name": "data",
            }
        ],
    )


def check_reporting_date_publication(self):
    response = self.app.get(f"/tenders/{self.tender_id}?acc_token={self.tender_token}")
    prev_qualification_end_date = response.json["data"]["qualificationPeriod"]["endDate"]
    response = self.app.get(f"/tenders/{self.tender_id}/qualifications?acc_token={self.tender_token}")
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    self.assertEqual(len(qualifications), 2)
    for qualification in qualifications:
        status = "active"
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
            {"data": {"status": status, "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], status)
    self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
    with freeze_time(prev_qualification_end_date):
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
            {"data": {"status": "active.pre-qualification.stand-still"}},
        )
    self.assertEqual(response.status, "200 OK")
    qualification_period = response.json["data"]["qualificationPeriod"]
    self.assertIn("reportingDatePublication", qualification_period)


# Tender2LotQualificationResourceTest


def lot_patch_tender_qualifications(self):
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualifications[2]["id"], self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualifications[1]["id"], self.tender_token),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualifications[0]["id"], self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")


def check_sign_doc_qualifications_before_stand_still(self):
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.status, "200 OK")
    qualifications = response.json["data"]
    for qualification in qualifications:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
    # try to move to stand-still status without docs
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "documents",
                "description": "Document with type 'evaluationReports' and format pkcs7-signature is required",
            }
        ],
    )
    # let's add sign doc
    sign_doc = {
        "title": "sign.p7s",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/pdf",
        "documentType": "evaluationReports",
    }
    # try to add 2 sign docs
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/documents?acc_token={self.tender_token}",
        {"data": [sign_doc, sign_doc]},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "evaluationReports document in tender should be only one",
    )

    # try to add doc without documentType
    sign_doc.pop("documentType", None)
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/documents?acc_token={self.tender_token}",
        {"data": sign_doc},
    )
    self.assertEqual(response.status, "201 Created")

    # try to add doc with another documentType in pre-qualification
    sign_doc["documentType"] = "notice"
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/documents?acc_token={self.tender_token}",
        {"data": sign_doc},
    )
    self.assertEqual(response.status, "201 Created")

    # add right document
    sign_doc["documentType"] = "evaluationReports"
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/documents?acc_token={self.tender_token}",
        {"data": sign_doc},
    )
    self.assertEqual(response.status, "201 Created")
    doc_1_id = response.json["data"]["id"]

    # patch relatedItem and documentOf in first doc
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/documents/{doc_1_id}?acc_token={self.tender_token}",
        {"data": {"documentOf": "lot", "relatedItem": self.initial_lots[1]["id"]}},
    )
    self.assertEqual(response.status, "200 OK")

    # try to move to stand-still status without docs for tender
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Document with type 'evaluationReports' and format pkcs7-signature is required",
    )

    # add sign doc for tender
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/documents?acc_token={self.tender_token}",
        {"data": sign_doc},
    )
    self.assertEqual(response.status, "201 Created")

    # move to stand-still successfully
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")

    # try to patch doc in active.pre-qualification.stand-still status
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/documents/{doc_1_id}?acc_token={self.tender_token}",
        {"data": {"title": "test"}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update document in current (active.pre-qualification.stand-still) tender status",
    )


def lot_patch_tender_qualifications_lots_none(self):
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"lots": [None]}}, status=422
    )
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "lots", "description": [["This field is required."]]}]
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"lots": None}}, status=422
    )
    self.assertIn(
        {"location": "body", "name": "items", "description": [{"relatedLot": ["relatedLot should be one of lots"]}]},
        response.json["errors"],
    )


def lot_get_tender_qualifications_collection(self):
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    self.assertEqual(len(qualifications), self.min_bids_number * 2)

    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    qualification_lots_ids = [q["lotID"] for q in qualifications]
    for bid in response.json["data"]:
        response = self.app.get(
            "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], self.initial_bids_tokens[bid["id"]])
        )
        for lotV in response.json["data"]["lotValues"]:
            lot_id = lotV["relatedLot"]
            self.assertIn(lot_id, qualification_lots_ids)
            qualification_lots_ids.remove(lot_id)


def tender_qualification_cancelled(self):
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    qualification_id = qualifications[0]["id"]
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification_id, self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't update qualification in current cancelled qualification status",
                "location": "body",
                "name": "data",
            }
        ],
    )

    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")

    new_qualifications = response.json["data"]
    self.assertEqual(len(new_qualifications), self.min_bids_number * 2 + 1)


# TenderQualificationDocumentResourceTest


def not_found(self):
    self.app.authorization = ("Basic", ("bot", "bot"))
    response = self.app.post_json(
        "/tenders/some_id/qualifications/some_id/documents",
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    response = self.app.post_json(
        "/tenders/{}/qualifications/some_id/documents".format(self.tender_id),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "qualification_id"}]
    )

    response = self.app.get("/tenders/some_id/qualifications/some_id/documents", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    response = self.app.get("/tenders/{}/qualifications/some_id/documents".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "qualification_id"}]
    )

    response = self.app.get("/tenders/some_id/qualifications/some_id/documents/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    response = self.app.get("/tenders/{}/qualifications/some_id/documents/some_id".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "qualification_id"}]
    )

    response = self.app.get(
        "/tenders/{}/qualifications/{}/documents/some_id".format(self.tender_id, self.qualifications[0]["id"]),
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "document_id"}])

    response = self.app.put_json(
        "/tenders/some_id/qualifications/some_id/documents/some_id",
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    response = self.app.put_json(
        "/tenders/{}/qualifications/some_id/documents/some_id".format(self.tender_id),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "qualification_id"}]
    )

    response = self.app.put_json(
        "/tenders/{}/qualifications/{}/documents/some_id".format(self.tender_id, self.qualifications[0]["id"]),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "document_id"}])

    self.app.authorization = ("Basic", ("bot", "bot"))
    response = self.app.put_json(
        "/tenders/{}/qualifications/{}/documents/some_id?acc_token={}".format(
            self.tender_id, self.qualifications[0]["id"], self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "document_id"}])


def tender_owner_create_qualification_document(self):
    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/documents?acc_token={}".format(
            self.tender_id, self.qualifications[0]["id"], self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.status, "201 Created")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.assertEqual("name.doc", response.json["data"]["title"])


def create_qualification_document(self):
    self.app.authorization = ("Basic", ("bot", "bot"))
    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/documents".format(self.tender_id, self.qualifications[0]["id"]),
        {
            "data": {
                "title": "name.doc",
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
    self.assertEqual("name.doc", response.json["data"]["title"])

    key = self.get_doc_id_from_url(response.json["data"]["url"])
    tender = self.mongodb.tenders.get(self.tender_id)
    qualification = [
        qualification
        for qualification in tender["qualifications"]
        if qualification["id"] == self.qualifications[0]["id"]
    ][0]
    self.assertIn(key, qualification["documents"][-1]["url"])

    # qualifications are public
    response = self.app.get(
        "/tenders/{}/qualifications/{}/documents".format(self.tender_id, self.qualifications[0]["id"])
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get(
        "/tenders/{}/qualifications/{}/documents?all=true".format(self.tender_id, self.qualifications[0]["id"])
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get(
        "/tenders/{}/qualifications/{}/documents/{}?download=some_id".format(
            self.tender_id, self.qualifications[0]["id"], doc_id
        ),
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "download"}])

    response = self.app.get(
        "/tenders/{}/qualifications/{}/documents/{}?download={}".format(
            self.tender_id, self.qualifications[0]["id"], doc_id, key
        )
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)

    response = self.app.get(
        "/tenders/{}/qualifications/{}/documents/{}".format(self.tender_id, self.qualifications[0]["id"], doc_id)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])


def create_tender_qualifications_document_json_bulk(self):
    self.app.authorization = ("Basic", ("bot", "bot"))

    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/documents".format(self.tender_id, self.qualifications[0]["id"]),
        {
            "data": [
                {
                    "title": "name1.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                },
                {
                    "title": "name2.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                },
            ]
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_1 = response.json["data"][0]
    doc_2 = response.json["data"][1]

    def assert_document(document, title):
        self.assertEqual(title, document["title"])
        self.assertIn("Signature=", document["url"])
        self.assertIn("KeyID=", document["url"])
        self.assertNotIn("Expires=", document["url"])

    assert_document(doc_1, "name1.doc")
    assert_document(doc_2, "name2.doc")

    response = self.app.get(
        "/tenders/{}/qualifications/{}/documents".format(self.tender_id, self.qualifications[0]["id"]),
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    doc_1 = response.json["data"][0]
    doc_2 = response.json["data"][1]
    assert_document(doc_1, "name1.doc")
    assert_document(doc_2, "name2.doc")


def put_qualification_document(self):
    self.app.authorization = ("Basic", ("bot", "bot"))

    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/documents".format(self.tender_id, self.qualifications[0]["id"]),
        {
            "data": {
                "title": "name.doc",
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

    # response = self.app.put_json(
    #     "/tenders/{}/qualifications/{}/documents/{}".format(self.tender_id, self.qualifications[0]["id"], doc_id),
    #     {"data": {
    #         "title": "name.doc",
    #         "url": self.generate_docservice_url(),
    #         "hash": "md5:" + "0" * 32,
    #         "format": "application/msword",
    #     }},
    #     status=404,
    # )
    # self.assertEqual(response.status, "404 Not Found")
    # self.assertEqual(response.content_type, "application/json")
    # self.assertEqual(response.json["status"], "error")
    # self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "body", "name": "file"}])

    response = self.app.put_json(
        "/tenders/{}/qualifications/{}/documents/{}".format(self.tender_id, self.qualifications[0]["id"], doc_id),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split("/")[-1].split("?")[0]
    tender = self.mongodb.tenders.get(self.tender_id)
    qualification = [
        qualification
        for qualification in tender["qualifications"]
        if qualification["id"] == self.qualifications[0]["id"]
    ][0]
    self.assertIn(key, qualification["documents"][-1]["url"])

    response = self.app.get(
        "/tenders/{}/qualifications/{}/documents/{}?download={}".format(
            self.tender_id, self.qualifications[0]["id"], doc_id, key
        )
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)

    response = self.app.get(
        "/tenders/{}/qualifications/{}/documents/{}".format(self.tender_id, self.qualifications[0]["id"], doc_id)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    response = self.app.put_json(
        "/tenders/{}/qualifications/{}/documents/{}".format(self.tender_id, self.qualifications[0]["id"], doc_id),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split("/")[-1].split("?")[0]
    tender = self.mongodb.tenders.get(self.tender_id)
    qualification = [
        qualification
        for qualification in tender["qualifications"]
        if qualification["id"] == self.qualifications[0]["id"]
    ][0]
    self.assertIn(key, qualification["documents"][-1]["url"])

    response = self.app.get(
        "/tenders/{}/qualifications/{}/documents/{}?download={}".format(
            self.tender_id, self.qualifications[0]["id"], doc_id, key
        )
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)

    with change_auth(self.app, ("Basic", ("broker", "broker"))):
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(
                self.tender_id, self.qualifications[0]["id"], self.tender_token
            ),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
    self.assertEqual(response.status, "200 OK")

    response = self.app.put_json(
        "/tenders/{}/qualifications/{}/documents/{}".format(self.tender_id, self.qualifications[0]["id"], doc_id),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't update document in current qualification status",
                "location": "body",
                "name": "data",
            }
        ],
    )


def delete_qualification_document(self):
    self.app.authorization = ("Basic", ("bot", "bot"))
    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/documents".format(self.tender_id, self.qualifications[0]["id"]),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]

    response = self.app.delete_json(
        "/tenders/{}/qualifications/{}/documents/{}".format(self.tender_id, self.qualifications[0]["id"], doc_id),
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [{"description": "Forbidden to delete document for qualification", "location": "body", "name": "data"}],
    )


def patch_qualification_document(self):
    self.app.authorization = ("Basic", ("bot", "bot"))

    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/documents".format(self.tender_id, self.qualifications[0]["id"]),
        {
            "data": {
                "title": "name.doc",
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

    response = self.app.get(
        "/tenders/{}/qualifications/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.qualifications[0]["id"], doc_id, self.tender_token
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/documents/{}".format(self.tender_id, self.qualifications[0]["id"], doc_id),
        {"data": {"documentOf": "lot"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["This field is required."], "location": "body", "name": "relatedItem"}],
    )

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/documents/{}".format(self.tender_id, self.qualifications[0]["id"], doc_id),
        {"data": {"documentOf": "lot", "relatedItem": "0" * 32}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["relatedItem should be one of lots"], "location": "body", "name": "relatedItem"}],
    )

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/documents/{}".format(self.tender_id, self.qualifications[0]["id"], doc_id),
        {"data": {"description": "document description"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get(
        "/tenders/{}/qualifications/{}/documents/{}".format(self.tender_id, self.qualifications[0]["id"], doc_id)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("document description", response.json["data"]["description"])

    with change_auth(self.app, ("Basic", ("broker", "broker"))):
        for qualification in self.qualifications:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(
                    self.tender_id, qualification["id"], self.tender_token
                ),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/documents/{}".format(self.tender_id, self.qualifications[0]["id"], doc_id),
        {"data": {"description": "document description2"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Can't update document in current qualification status"}],
    )

    with change_auth(self.app, ("Basic", ("broker", "broker"))):
        self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"status": "active.pre-qualification.stand-still"}},
        )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/documents/{}".format(self.tender_id, self.qualifications[0]["id"], doc_id),
        {"data": {"description": "document description2"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can't update document in current (active.pre-qualification.stand-still) tender status",
            }
        ],
    )


def create_qualification_document_after_status_change(self):
    for i in range(self.min_bids_number - 1):
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(
                self.tender_id, self.qualifications[i]["id"], self.tender_token
            ),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")

    with change_auth(self.app, ("Basic", ("bot", "bot"))):
        response = self.app.post_json(
            "/tenders/{}/qualifications/{}/documents".format(self.tender_id, self.qualifications[0]["id"]),
            {
                "data": {
                    "title": "name.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
            status=403,
        )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't add document in current qualification status",
                "location": "body",
                "name": "data",
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(
            self.tender_id, self.qualifications[-1]["id"], self.tender_token
        ),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")

    with change_auth(self.app, ("Basic", ("bot", "bot"))):
        response = self.app.post_json(
            "/tenders/{}/qualifications/{}/documents".format(self.tender_id, self.qualifications[-1]["id"]),
            {
                "data": {
                    "title": "name.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
            status=403,
        )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't add document in current qualification status",
                "location": "body",
                "name": "data",
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(
            self.tender_id, self.qualifications[-1]["id"], self.tender_token
        ),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    with change_auth(self.app, ("Basic", ("bot", "bot"))):
        response = self.app.post_json(
            "/tenders/{}/qualifications/{}/documents".format(self.tender_id, self.qualifications[-1]["id"]),
            {
                "data": {
                    "title": "name.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
            status=403,
        )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't add document in current qualification status",
                "location": "body",
                "name": "data",
            }
        ],
    )

    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.status, "200 OK")
    self.qualifications = response.json["data"]
    self.assertEqual(len(self.qualifications), self.min_bids_number + 1)

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(
            self.tender_id, self.qualifications[self.min_bids_number]["id"], self.tender_token
        ),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")

    self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")

    with change_auth(self.app, ("Basic", ("bot", "bot"))):
        response = self.app.post_json(
            "/tenders/{}/qualifications/{}/documents".format(
                self.tender_id, self.qualifications[self.min_bids_number]["id"]
            ),
            {
                "data": {
                    "title": "name.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
            status=403,
        )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't add document in current (active.pre-qualification.stand-still) tender status",
                "location": "body",
                "name": "data",
            }
        ],
    )


def put_qualification_document_after_status_change(self):
    with change_auth(self.app, ("Basic", ("bot", "bot"))):
        response = self.app.post_json(
            "/tenders/{}/qualifications/{}/documents".format(self.tender_id, self.qualifications[0]["id"]),
            {
                "data": {
                    "title": "name.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )
    self.assertEqual(response.status, "201 Created")
    doc_id = response.json["data"]["id"]

    for qualification in self.qualifications:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

    self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")

    with change_auth(self.app, ("Basic", ("bot", "bot"))):
        response = self.app.put_json(
            "/tenders/{}/qualifications/{}/documents/{}".format(self.tender_id, self.qualifications[0]["id"], doc_id),
            {
                "data": {
                    "title": "name.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
            status=403,
        )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't update document in current (active.pre-qualification.stand-still) tender status",
                "location": "body",
                "name": "data",
            }
        ],
    )


def switch_bid_status_unsuccessul_to_active(self):
    bid_id, bid_token = list(self.initial_bids_tokens.items())[0]

    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    self.assertEqual(len(qualifications), 4)
    qualification_id = ""
    for qualification in qualifications:
        status = "active"
        if qualification["bidID"] == bid_id:
            status = "unsuccessful"
            qualification_id = qualification["id"]
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
            {"data": {"status": status, "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], status)
    self.add_sign_doc(self.tender_id, self.tender_token, document_type="evaluationReports")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification"}},
    )
    self.assertEqual(response.status, "200 OK")

    # Cancel qualification
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification_id, self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    new_qualification_id = response.headers["location"].split("/")[-1]
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, new_qualification_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    for b in response.json["data"]:
        self.assertEqual(b["status"], "active")


def create_qualification_requirement_response(self):
    self.app.authorization = ("Basic", ("broker", ""))

    base_request_path = "/tenders/{}/qualifications/{}/requirement_responses".format(
        self.tender_id, self.qualification_id
    )
    request_path = "{}?acc_token={}".format(base_request_path, self.tender_token)

    valid_data = [
        {
            "requirement": {
                "id": self.requirement_id,
            },
            "value": True,
        }
    ]

    response = self.app.post_json(
        base_request_path,
        {"data": valid_data},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(response.json["errors"], [{"description": "Forbidden", "location": "url", "name": "permission"}])

    response = self.app.post_json(
        "{}?acc_token={}".format(base_request_path, "some_random_token"),
        {"data": valid_data},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(response.json["errors"], [{"description": "Forbidden", "location": "url", "name": "permission"}])

    response = self.app.post_json(
        request_path,
        {
            "data": [
                {
                    "requirement": {
                        "id": self.requirement_id,
                    }
                }
            ]
        },
        status=422,
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "requirementResponses.0",
                "description": {"value": 'Response required at least one of field ["value", "values"]'},
            },
        ],
    )

    response = self.app.post_json(
        request_path,
        {"data": [{"value": 10}]},
        status=422,
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [
            {"location": "body", "name": "requirement", "description": ["This field is required."]},
        ],
    )

    response = self.app.post_json(request_path, {"data": valid_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    rrs = response.json["data"]
    self.assertIn("classification", rrs[0])
    self.assertIn("title", rrs[0]["requirement"])
    clean_requirement_responses(rrs)

    for i, rr_data in enumerate(valid_data):
        for k, v in rr_data.items():
            if k == "value":
                self.assertEqual(str(rrs[i][k]), str(v))
            else:
                self.assertEqual(rrs[i][k], v)

    response = self.app.get(
        f"/tenders/{self.tender_id}/qualifications/{self.qualification_id}?acc_token={self.tender_token}"
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    rrs = response.json["data"]["requirementResponses"]
    self.assertIn("classification", rrs[0])
    self.assertIn("title", rrs[0]["requirement"])


def patch_qualification_requirement_response(self):
    base_request_path = "/tenders/{}/qualifications/{}/requirement_responses".format(
        self.tender_id, self.qualification_id
    )
    request_path = "{}?acc_token={}".format(base_request_path, self.tender_token)

    valid_data = [
        {
            "requirement": {
                "id": self.requirement_id,
            },
            "value": True,
        }
    ]

    response = self.app.post_json(request_path, {"data": valid_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    rr_id = response.json["data"][0]["id"]

    base_request_path = "/tenders/{}/qualifications/{}/requirement_responses/{}".format(
        self.tender_id, self.qualification_id, rr_id
    )
    request_path = "{}?acc_token={}".format(base_request_path, self.tender_token)
    updated_data = {
        "value": 100,
    }

    auth = self.app.authorization
    self.app.authorization = ("Basic", ("broker", ""))

    response = self.app.patch_json(
        base_request_path,
        {"data": updated_data},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(response.json["errors"], [{"description": "Forbidden", "location": "url", "name": "permission"}])

    response = self.app.patch_json(
        "{}?acc_token={}".format(base_request_path, "some_random_token"),
        {"data": updated_data},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(response.json["errors"], [{"description": "Forbidden", "location": "url", "name": "permission"}])

    self.app.authorization = auth
    response = self.app.patch_json(request_path, {"data": updated_data}, status=422)

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["Must be either true or false."], "location": "body", "name": "value"}],
    )


def get_qualification_requirement_response(self):
    base_request_path = "/tenders/{}/qualifications/{}/requirement_responses".format(
        self.tender_id, self.qualification_id
    )
    request_path = "{}?acc_token={}".format(base_request_path, self.tender_token)

    valid_data = [
        {
            "requirement": {
                "id": self.requirement_id,
            },
            "value": True,
        }
    ]

    response = self.app.post_json(request_path, {"data": valid_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    rr_id = response.json["data"][0]["id"]

    response = self.app.get(
        "/tenders/{}/qualifications/{}/requirement_responses".format(self.tender_id, self.qualification_id)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    rrs = response.json["data"]
    clean_requirement_responses(rrs)
    self.assertEqual(len(rrs), 1)

    for i, rr_data in enumerate(valid_data):
        for k, v in rr_data.items():
            self.assertIn(k, rrs[i])
            self.assertEqual(v, rrs[i][k])

    response = self.app.get(
        "/tenders/{}/qualifications/{}/requirement_responses/{}".format(self.tender_id, self.qualification_id, rr_id)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    rr = response.json["data"]
    clean_requirement_responses([rr])
    for k, v in valid_data[0].items():
        self.assertIn(k, rr)
        self.assertEqual(v, rr[k])


def create_qualification_requirement_response_evidence(self):
    base_request_path = "/tenders/{}/qualifications/{}/requirement_responses/{}/evidences".format(
        self.tender_id, self.qualification_id, self.rr_id
    )
    request_path = "{}?acc_token={}".format(base_request_path, self.tender_token)

    auth = self.app.authorization
    self.app.authorization = ("Basic", ("broker", ""))

    valid_data = {
        "title": "Requirement response",
        "relatedDocument": {
            "id": self.doc_id,
            "title": "name.doc",
        },
        "type": "document",
    }

    response = self.app.post_json(
        base_request_path,
        {"data": valid_data},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(response.json["errors"], [{"description": "Forbidden", "location": "url", "name": "permission"}])

    response = self.app.post_json(
        "{}?acc_token={}".format(base_request_path, "some_random_token"),
        {"data": valid_data},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(response.json["errors"], [{"description": "Forbidden", "location": "url", "name": "permission"}])

    self.app.authorization = auth
    response = self.app.post_json(
        request_path,
        {
            "data": {
                "title": "Some title",
                "description": "some description",
            }
        },
        status=422,
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [{"description": ["type should be one of eligibleEvidences types"], "location": "body", "name": "type"}],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "title": "Some title",
                "description": "some description",
                "type": "document",
            }
        },
        status=422,
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [{"description": ["This field is required."], "location": "body", "name": "relatedDocument"}],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "title": "Some title",
                "description": "some description",
                "type": "document",
                "relatedDocument": {
                    "id": "0" * 32,
                    "title": "test.doc",
                },
            }
        },
        status=422,
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["relatedDocument.id should be one of qualification documents"],
                "location": "body",
                "name": "relatedDocument",
            }
        ],
    )

    response = self.app.post_json(request_path, {"data": valid_data})

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    evidence = response.json["data"]

    for k, v in valid_data.items():
        self.assertIn(k, evidence)
        self.assertEqual(evidence[k], v)


def patch_qualification_requirement_response_evidence(self):
    valid_data = {
        "title": "Requirement response",
        "relatedDocument": {
            "id": self.doc_id,
            "title": "name.doc",
        },
        "type": "document",
    }

    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/requirement_responses/{}/evidences?acc_token={}".format(
            self.tender_id, self.qualification_id, self.rr_id, self.tender_token
        ),
        {"data": valid_data},
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    evidence_id = response.json["data"]["id"]

    updated_data = {
        "title": "Updated title",
        "description": "Updated description",
    }

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/requirement_responses/{}/evidences/{}?acc_token={}".format(
            self.tender_id, self.qualification_id, self.rr_id, evidence_id, self.tender_token
        ),
        {"data": updated_data},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    evidence = response.json["data"]

    self.assertEqual(evidence["title"], updated_data["title"])
    self.assertEqual(evidence["description"], updated_data["description"])


def get_qualification_requirement_response_evidence(self):
    valid_data = {
        "title": "Requirement response",
        "relatedDocument": {
            "id": self.doc_id,
            "title": "name.doc",
        },
        "type": "document",
    }

    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/requirement_responses/{}/evidences?acc_token={}".format(
            self.tender_id, self.qualification_id, self.rr_id, self.tender_token
        ),
        {"data": valid_data},
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    evidence_id = response.json["data"]["id"]

    response = self.app.get(
        "/tenders/{}/qualifications/{}/requirement_responses/{}/evidences".format(
            self.tender_id, self.qualification_id, self.rr_id
        )
    )

    evidences = response.json["data"]
    self.assertEqual(len(evidences), 1)

    for k, v in valid_data.items():
        self.assertIn(k, evidences[0])
        self.assertEqual(v, evidences[0][k])

    response = self.app.get(
        "/tenders/{}/qualifications/{}/requirement_responses/{}/evidences/{}".format(
            self.tender_id, self.qualification_id, self.rr_id, evidence_id
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    rr = response.json["data"]
    for k, v in valid_data.items():
        self.assertIn(k, rr)
        self.assertEqual(v, rr[k])
