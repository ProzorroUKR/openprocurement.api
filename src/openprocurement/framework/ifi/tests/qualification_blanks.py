def qualification_active_without_documents(self):
    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(self.submission_id, self.submission_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    qualification_id = response.json["data"]["qualificationID"]

    response = self.app.patch_json(
        f"/qualifications/{qualification_id}?acc_token={self.framework_token}",
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get(f"/frameworks/{self.framework_id}")
    self.assertIn("agreementID", response.json["data"])


def qualification_unsuccessful_without_documents(self):
    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(self.submission_id, self.submission_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    qualification_id = response.json["data"]["qualificationID"]

    response = self.app.patch_json(
        f"/qualifications/{qualification_id}?acc_token={self.framework_token}",
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def qualification_evaluation_reports_documents_quantity(self):
    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(self.submission_id, self.submission_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    qualification_id = response.json["data"]["qualificationID"]

    data = {
        "documents": [
            {
                "id": "e4d7216f28dc4a1cbf18c5e4ee2cd1c5",
                "title": "sign.p7s",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentType": "evaluationReports",
            },
            {
                "title": "evalouationReports.p7s",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentType": "evaluationReports",
            },
        ],
    }

    response = self.app.patch_json(
        f"/qualifications/{qualification_id}?acc_token={self.framework_token}",
        {"data": data},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "evaluationReports document in qualification should be only one",
    )

    response = self.app.post_json(
        f"/qualifications/{qualification_id}/documents?acc_token={self.framework_token}",
        {"data": data["documents"]},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "evaluationReports document in qualification should be only one",
    )

    response = self.app.post_json(
        f"/qualifications/{qualification_id}/documents?acc_token={self.framework_token}",
        {"data": data["documents"][0]},
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.post_json(
        f"/qualifications/{qualification_id}/documents?acc_token={self.framework_token}",
        {"data": data["documents"][0]},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "evaluationReports document in qualification should be only one",
    )

    response = self.app.patch_json(
        f"/qualifications/{qualification_id}?acc_token={self.framework_token}",
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")
