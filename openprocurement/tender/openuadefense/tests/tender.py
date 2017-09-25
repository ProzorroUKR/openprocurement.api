# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.api.tests.base import BaseWebTest

from openprocurement.tender.belowthreshold.tests.base import test_lots
from openprocurement.tender.belowthreshold.tests.tender import TenderResourceTestMixin
from openprocurement.tender.belowthreshold.tests.tender_blanks import (
    # TenderUAProcessTest
    invalid_tender_conditions,
)

from openprocurement.tender.openua.tests.tender import TenderUaProcessTestMixin
from openprocurement.tender.openua.tests.tender_blanks import (
    # TenderUAResourceTest
    empty_listing,
    create_tender_generated,
)

from openprocurement.tender.openuadefense.tests.base import (
    BaseTenderUAWebTest,
    test_tender_data,
)
from openprocurement.tender.openuadefense.tests.tender_blanks import (
    # TenderUATest
    simple_add_tender,
    # TenderUAResourceTest
    create_tender_invalid,
    patch_tender,
    patch_tender_ua,
    # TenderUAProcessTest
    one_valid_bid_tender_ua,
    one_invalid_bid_tender,
)


class TenderUATest(BaseWebTest):

    initial_data = test_tender_data

    test_simple_add_tender = snitch(simple_add_tender)


class TenderUAResourceTest(BaseTenderUAWebTest, TenderResourceTestMixin):
    test_lots_data = test_lots  # TODO: change attribute identifier

    initial_data = test_tender_data

    test_empty_listing = snitch(empty_listing)
    test_create_tender_invalid = snitch(create_tender_invalid)
    test_create_tender_generated = snitch(create_tender_generated)
    test_patch_tender = snitch(patch_tender)
    test_patch_tender_ua = snitch(patch_tender_ua)


class TenderUAProcessTest(BaseTenderUAWebTest, TenderUaProcessTestMixin):
    initial_data = test_tender_data

    test_invalid_tender_conditions = snitch(invalid_tender_conditions)
    test_one_valid_bid_tender_ua = snitch(one_valid_bid_tender_ua)
    test_one_invalid_bid_tender = snitch(one_invalid_bid_tender)

    def test_patch_not_author(self):
        response = self.app.post_json('/tenders', {'data': test_tender_data})
        self.assertEqual(response.status, '201 Created')
        tender = response.json['data']
        owner_token = response.json['access']['token']

        authorization = self.app.authorization
        self.app.authorization = ('Basic', ('bot', 'bot'))

        response = self.app.post('/tenders/{}/documents'.format(tender['id']),
                                 upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])

        self.app.authorization = authorization
        response = self.app.patch_json('/tenders/{}/documents/{}?acc_token={}'.format(tender['id'], doc_id, owner_token),
                                       {"data": {"description": "document description"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can update document only author")

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderUAProcessTest))
    suite.addTest(unittest.makeSuite(TenderUAResourceTest))
    suite.addTest(unittest.makeSuite(TenderUATest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
