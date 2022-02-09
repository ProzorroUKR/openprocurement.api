

def create_document_active_tendering_status(self):

    self.set_status("active.tendering")
    # TODO: check if document should not be updated in this |\ status,
    # because now there is no status validation

    response = self.app.post_json(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {
            "title": "укр.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

