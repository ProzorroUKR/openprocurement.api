# -*- coding: utf-8 -*-
from email.header import Header

# TenderDocumentResourceTest
from mock import patch
from openprocurement.tender.core.tests.base import bad_rs_request, srequest


def create_document_active_tendering_status(self):

    self.set_status("active.tendering")
    # TODO: check if document should not be updated in this |\ status,
    # because now there is no status validation

    response = self.app.post(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        upload_files=[("file", u"укр.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    # self.assertEqual(
    #     response.json["errors"][0]["description"], "Can't add document in current (active.tendering) tender status"
    # )
