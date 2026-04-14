def create_acceptance_report_document_pre_qualification(self):
    # acceptanceReport should be allowed in active.pre-qualification for ARMA
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
