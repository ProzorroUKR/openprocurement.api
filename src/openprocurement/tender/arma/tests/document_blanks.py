def create_acceptance_report_document_pre_qualification(self):
    # acceptanceReport is allowed in active.pre-qualification for ARMA
    response = self.app.post_json(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": "acceptance_report.p7s",
                "documentType": "acceptanceReport",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["documentType"], "acceptanceReport")
    doc_id = response.json["data"]["id"]

    # Second acceptanceReport on the same tender is rejected
    response = self.app.post_json(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": "acceptance_report_2.p7s",
                "documentType": "acceptanceReport",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "acceptanceReport document in tender should be only one",
    )

    # PUT of acceptanceReport document ignores changes to documentType and format
    response = self.app.put_json(
        "/tenders/{}/documents/{}?acc_token={}".format(self.tender_id, doc_id, self.tender_token),
        {
            "data": {
                "title": "acceptance_report_v2.p7s",
                "documentType": "biddingDocuments",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["documentType"], "acceptanceReport")
    self.assertEqual(response.json["data"]["format"], "application/pkcs7-signature")
